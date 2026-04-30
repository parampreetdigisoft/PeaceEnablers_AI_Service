# =========================================================================== #
#  rag_query_service.py  (refactored)                                         #
# =========================================================================== #
"""
RAGQueryService  (refactored)
------------------------------
Two-stage RAG pipeline for country document Q&A.

Stage 1 — LLM-driven TOC routing  (which sections are relevant?)
Stage 2 — ChromaDB vector search within those sections

LLM calls are handled by LLMBaseService.
All prompt text comes from PEMPromptTemplates.
"""
from datetime import datetime
import os
import re
import chromadb
import logging
import json
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from app.services.common.llm_base_service import LLMBaseService
from app.services.common.country_prompt import PEMPromptTemplates
from app.services.core.repository import DatabaseRepository

logger = logging.getLogger(__name__)

CHROMA_PATH = "./chroma_store"


class RAGQueryService:
    """
    Hybrid RAG service: LLM-routed TOC selection + ChromaDB vector retrieval.

    LLM mechanics live in LLMBaseService (injected).
    Prompt text lives in PEMPromptTemplates.
    """

    def __init__(self) -> None:

        # Ensure directory exists
        if not os.path.exists(CHROMA_PATH):
            os.makedirs(CHROMA_PATH)

        try:
            self.client = chromadb.PersistentClient(
                path=CHROMA_PATH,
                settings=chromadb.config.Settings(anonymized_telemetry=False),
            )

        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            raise

        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self._db = DatabaseRepository()
        # --- LLM (shared base service) ---
        self._llm_svc = LLMBaseService(max_retries=3, retry_delay=1.0)

    # ------------------------------------------------------------------ #
    #  Initialisation                                                      #
    # ------------------------------------------------------------------ #

    async def initialize(self) -> None:
        """Initialise the shared LLM service."""
        await self._llm_svc.initialize()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    async def get_country_document_context(
        self,
        country_id: int,
        msg_text: str,
        pillar_id: Optional[int] = None,
    ) -> str:
        """
        Answer a natural-language question about a country using:
          1. LLM-selected TOC sections
          2. ChromaDB vector search within those sections
          3. LLM synthesis of retrieved chunks + chat history
        """
        # Stage 1 — TOC routing
        toc = await self._get_country_toc(country_id, pillar_id)

        relevant_toc_ids = []
        if len(toc) > 4:
            relevant_toc_ids = await self._route_via_toc(msg_text, toc)
        else:
            relevant_toc_ids = [row["TOCID"] for row in toc]

        # Stage 2 — Vector retrieval
        chunks = self._fetch_relevant_chunks(
            country_id=country_id,
            question=msg_text,
            toc_ids=relevant_toc_ids,
            top_k=10,
            pillar_id=pillar_id,
        )

        # Build context and history strings
        local_context = self._build_context_block(chunks)

        return local_context

    async def answer_country_question(
        self,
        country_id: int,
        question: str,
        pillar_id: Optional[int] = None,
    ) -> str:
        """
        Answer a natural-language question about a country using:
          1. LLM-selected TOC sections
          2. ChromaDB vector search within those sections
          3. LLM synthesis of retrieved chunks + chat history
          
        """
        # Stage 1 — TOC routing
        toc = await self._get_country_toc(country_id, pillar_id)

        relevant_toc_ids = []
        if len(toc) > 4:
            relevant_toc_ids = await self._route_via_toc(question, toc)
        else:
            relevant_toc_ids = [row["TOCID"] for row in toc]

        # Stage 2 — Vector retrieval
        chunks = self._fetch_relevant_chunks(
            country_id=country_id,
            question=question,
            toc_ids=relevant_toc_ids,
            top_k=5,
            pillar_id=pillar_id,
        )

        # Build context and history strings
        local_context = self._build_context_block(chunks)
        year = datetime.now().year      
        ai_country= await self._db.get_ai_country_context(country_id, year)

        if len(local_context)  < 50 :
           
            local_context = "\n".join(f"{key}: {value}" for key, value in ai_country.items())

        history_str =""
        pillar_name =""
        countryName =ai_country["CountryName"]

        # Stage 3 — LLM answer synthesis
        answer = await self._llm_svc.invoke_messages(
            messages=[
                {
                    "role": "system",
                    "content": PEMPromptTemplates.rag_answer_system_prompt(),
                },
                {
                    "role": "user",
                    "content": PEMPromptTemplates.rag_answer_user_prompt(
                        local_context, history_str, question,
                        countryName, pillar_name
                    ),
                },
            ],
            label=f"rag_answer|country{country_id}",
        )

        return answer

    # ------------------------------------------------------------------ #
    #  Stage 1 — DB: fetch TOC                                           #
    #  ⚡ Tenant migration point: only this method touches the DB        #
    # ------------------------------------------------------------------ #

    async def _get_country_toc(
        self,
        country_id: int,
        pillar_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Fetch the Table-of-Contents entries for a country's uploaded documents.

        Returns a list of dicts with keys:
            TOCID, SectionPath, SectionTitle, SectionLevel, PillarID, FileName
        """
        query = """
            SELECT t.TOCID, t.SectionPath, t.SectionTitle, t.SectionLevel,
                   t.PillarID, cd.FileName
            FROM DocumentTOC t
            JOIN CountryDocuments cd ON cd.CountryDocumentID = t.CountryDocumentID
            WHERE t.CountryID = ? AND cd.IsDeleted = 0
        """
        # Future: add   AND t.TenantID = ?   when multi-tenant
        return await self._db.engine.fetch_dicts_async(query, (country_id,))

    # ------------------------------------------------------------------ #
    #  Stage 1 — LLM: route question to relevant TOC sections            #
    # ------------------------------------------------------------------ #

    async def _route_via_toc(
        self,
        question: str,
        toc: List[Dict],
    ) -> List[int]:
        """
        Ask the LLM which TOC section IDs are most relevant to the question.
        Returns a list of TOCID integers (may be empty).
        """
        if not toc:
            return []

        toc_text = "\n".join(
            f"[{row['TOCID']}] (Level {row['SectionLevel']}) {row['SectionPath']}"
            for row in toc
        )
        prompt = PEMPromptTemplates.rag_routing_prompt(toc_text, question)
        raw = await self._llm_svc.invoke_raw(
            prompt, label=f"rag_routing|q={question[:40]}"
        )

        match = re.search(r"\[[\d,\s]*\]", raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return []

    # ------------------------------------------------------------------ #
    #  Stage 2 — ChromaDB: vector search within sections                 #
    # ------------------------------------------------------------------ #

    def _fetch_relevant_chunks(
        self,
        country_id: int,
        question: str,
        toc_ids: List[int],
        top_k: int = 5,
        pillar_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Run a vector similarity search against the ChromaDB collection and
        return the top-k chunks, optionally filtered to the routed TOC IDs.
        """
        collection_name = f"country_{country_id}"
        try:
            #    collections = self.client.list_collections()

            collection = self.client.get_collection(
                name=collection_name, embedding_function=self.embed_fn
            )
        except Exception as e:
            logger.error(f"Error fetching collection {collection_name}: {e}")
            return []

        where_filter = {"toc_id": {"$in": toc_ids}} if toc_ids else None
        results = collection.query(
            query_texts=[question],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append(
                {
                    "text": doc,
                    "section": meta.get("section_path", ""),
                    "file": meta.get("section_title", ""),
                    "relevance": round(1 - dist, 3),
                }
            )
        return chunks

    # ------------------------------------------------------------------ #
    #  Helpers                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _build_context_block(chunks: List[Dict]) -> str:
        if not chunks:
            return ""
        lines = ["=== FROM UPLOADED COUNTRY DOCUMENTS ==="]
        for chunk in chunks:
            lines.append(f"[{chunk['section']}]\n{chunk['text']}\n")
        return "\n".join(lines)

    @staticmethod
    def _build_history_str(chat_history: Optional[List[Dict]]) -> str:
        if not chat_history:
            return ""
        lines = []
        for msg in chat_history[-6:]:  # last 3 turns (user + assistant × 3)
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)


rag_query_service = RAGQueryService()
