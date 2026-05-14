# =========================================================================== #
#  chat_service.py  (refactored)                                         #
# =========================================================================== #

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from app.services.common import pillar_prompts
from app.services.core.repository import DatabaseRepository
from app.services.rag_query_service import rag_query_service
from app.services.common.llm_base_service import LLMBaseService
from app.services.common import json_response_parser as jrp
from app.services.common.pillar_prompts import PeaceEnablerPillarPrompts
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
                relevant_faq_ids = relevant_faq_ids[: 3 if historyText == None else 2]
                ai_context = await self._db.GetLocalContextDataForLLM(relevant_faq_ids,country_id,pillar_id)
            else:
                ai_context = await rag_query_service.get_country_document_context(country_id,questionText, pillar_id)
        else:
            ai_context = await self._db.GetLocalContextDataForLLM([faqid],country_id,pillar_id)
            
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
            faqs = await self._db.get_FAQ_context(True)
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

    
    async def answer_crossComparision(
        self,
        questionText: str,
        countryIDs: list[int],
        historyText: Optional[str] = None,
    ) -> str:

        year = datetime.now().year

        countries = []

        if len(countryIDs) > 0:
            query = f"""
                SELECT CountryName, Continent
                FROM Countries
                WHERE CountryID IN ({",".join(map(str, countryIDs))})
            """

            countries = await self._db.engine.fetch_dicts_async(query)

        relevant_faq_ids = []

        if len(countryIDs) == 0:
            faqs = await self._db.get_FAQ_context(True)
            relevant_faq_ids = await rag_query_service.get_related_FAQ_IDs(
                questionText,
                faqs
            )
        else:
            relevant_faq_ids = countryIDs

        if len(relevant_faq_ids) > 0:
            ai_context = await self._db.GetCrossComparisionLocalContextDataForLLM(
                relevant_faq_ids
            )
        else:
            ai_context = await rag_query_service.get_global_document_context(
                questionText
            )

        countryName = ", ".join(
            [country["CountryName"] for country in countries]
        )

        pillar_name = "Get pillars from provided context"

        answer = await rag_query_service.send_question_to_llm(
            questionText,
            ai_context,
            countryName,
            pillar_name,
            historyText
        )

        return answer
    

    async def answer_Country_executive_slides( self, country_id: int) -> Dict[str, Any]:

        try:

            year = datetime.now().year

            # ---------------------------------------------------------
            # country CONTEXT
            # ---------------------------------------------------------
            ai_country = await self._db.get_ai_country_context(
                country_id,
                year
            )

            if not ai_country:
                return {
                    "success": False,
                    "message": "country context not found"
                }

            country_name = ai_country["CountryName"]
            country = ai_country["CountryName"]

            ai_country_context = "\n".join(
                f"{key}: {value}"
                for key, value in ai_country.items()
            )

            # ---------------------------------------------------------
            # DEFAULT EXECUTIVE QUESTION
            # ---------------------------------------------------------
            questionText = f"""
            Generate a country-wide executive intelligence briefing
            for {country_name}.

            Analyze:
            - current operational conditions
            - governance effectiveness
            - infrastructure performance
            - healthcare pressure
            - environmental risks
            - social cohesion
            - housing instability
            - economic pressure
            - institutional resilience
            - public safety conditions

            Identify:
            - immediate operational concerns
            - worsening trends
            - stabilization signals
            - top country-wide risks
            - emerging threats
            - future escalation risks

            Focus on cross-pillar intelligence synthesis
            and executive situational awareness.
            """

            # ---------------------------------------------------------
            # DOCUMENT CONTEXT
            # ---------------------------------------------------------
            document_context = await rag_query_service.get_country_document_context(
                country_id,
                questionText
            )

            all_pillar_contexts = PeaceEnablerPillarPrompts.get_all_pillar_names()

            # ---------------------------------------------------------
            # CALL RAG SERVICE
            # ---------------------------------------------------------
            ai_result  = await rag_query_service.country_executive_slides(
                country_name=country_name,
                country=country,
                ai_country_context=ai_country_context,
                documentContext=document_context,
                allPillarContexts=all_pillar_contexts,
                year=year
            )


            if not ai_result.get("success"):
                return {
                    "success": False,
                    "message": "Failed to generate executive slides"
                }

            data = ai_result["data"]

            # ---------------------------------------------------------
            # FINAL RESPONSE
            # ---------------------------------------------------------
            result = {
                "countryId": country_id,
                "countryName": data.get("countryName"),

                "dailyPerformance": {
                    "trend": data["daily"]["trend"],
                    "summary": data["daily"]["summary"]
                },

                "weeklyPerformance": {
                    "trend": data["weekly"]["trend"],
                    "summary": data["weekly"]["summary"]
                },

                "monthlyPerformance": {
                    "trend": data["monthly"]["trend"],
                    "summary": data["monthly"]["summary"]
                },

                "combinedRisks": data["combinedRisks"]["risks"],

                "earlyWarnings": data["earlyWarnings"]["warnings"]
            }

            return {
                "success": True,
                "message": "Executive slides generated successfully",
                "result": result
            }

        except Exception as exc:

            logger.exception(
                "answer_country_executive_slides_question failed"
            )

            return {
                "success": False,
                "error": str(exc)
            }
        

chat_service = ChatService()
