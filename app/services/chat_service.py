# =========================================================================== #
#  chat_service.py  (refactored)                                         #
# =========================================================================== #

import logging
from typing import Optional
from datetime import datetime
from app.services.core.repository import DatabaseRepository
from app.services.rag_query_service import rag_query_service
from app.services.common.llm_base_service import LLMBaseService

logger = logging.getLogger(__name__)
CHROMA_PATH = "./chroma_store"


class ChatService:


    def __init__(self) -> None:
        self._db = DatabaseRepository()
        self._llm_svc = LLMBaseService(max_retries=3, retry_delay=1.0)

    async def initialize(self) -> None:
        """Initialise the shared LLM service."""
        await self._llm_svc.initialize()

    # ------------------------------------------------------------------ #
    #  Public Methods                                                    #
    # ------------------------------------------------------------------ #

    async def answer_country_question (
        self,
        country_id: int,
        questionText: str,
        historyText: Optional[str] = None,
        faqid : Optional[int] = None,
        pillar_id: Optional[int] = None,
    ) -> str:
        year = datetime.now().year      

        ai_country_context = await self._db.get_ai_country_context(country_id, year,pillar_id)

        if faqid is None :
            faqs = await self._db.get_FAQ_context()
            relevant_faq_ids = await rag_query_service.get_related_FAQ_IDs(questionText, faqs)

            if len(relevant_faq_ids)>0:
                ai_context = await self._db.GetLocalContextDataForLLM(relevant_faq_ids,country_id,pillar_id)
            else:
                ai_context = await rag_query_service.get_country_document_context(country_id,questionText, pillar_id)
        else:
            ai_context = await self._db.usp_GetCountryDataForLLM(country_id,[faqid],pillar_id)
            
        if len(ai_context) < 1:
            ai_context = "\n".join(f"{key}: {value}" for key, value in ai_country_context.items())
        pillar_name =ai_country_context["PillarName"]
        countryName =ai_country_context["CountryName"]

        answer = await rag_query_service.send_question_to_llm(questionText,ai_context,countryName,pillar_name,historyText)

        return answer
    
    async def answer_global_question (
        self,
        questionText: str,
        historyText: Optional[str] = None,
        faqid: Optional[int] = None
    ) -> str:
        year = datetime.now().year    
        
        relevant_faq_ids =[]
        if faqid is None: 
            query = """
                select 
                FAQID,Related,Category,QuestionText 
                from AIAssistantFAQ 
                where Related like '%global%'
            """
            faqs = await self._db.engine.fetch_dicts_async(query)

            relevant_faq_ids = await rag_query_service.get_related_FAQ_IDs(questionText, faqs)
        else :
            relevant_faq_ids=[faqid]
            
        if len(relevant_faq_ids)>0:
            ai_context = await self._db.GetLocalContextDataForLLM(relevant_faq_ids)
        else:
            ai_context = await rag_query_service.get_global_document_context(questionText)

        countryName="global for all countries"
        pillar_name=""            

        answer = await rag_query_service.send_question_to_llm(questionText, ai_context, countryName, pillar_name, historyText)

        return answer

chat_service = ChatService()
