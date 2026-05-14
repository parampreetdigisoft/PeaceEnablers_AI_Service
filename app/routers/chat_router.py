"""
Score analysis Router - API endpoints with database exception logging
Fire-and-forget pattern for long-running analysis tasks
"""
import logging
from fastapi import APIRouter, HTTPException
from app.view_models.ChatRequest import ChatCountryExecutiveSlidesRequest, ChatCountryExecutiveSlidesResponse, ChatCountryRequest, ChatCrossComparisionRequest, ChatGlobalRequest, ChatRequest
from app.view_models.AnalysisRequest import ChatResponse
logger = logging.getLogger(__name__)
from app.services.chat_service import chat_service


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask(request: ChatRequest):
    """
    Chat endpoint:
    - Accepts user question in body
    - Runs RAG pipeline
    - Returns AI-generated answer
    """
    try:
        result = await chat_service.answer_country_question (
            country_id = request.countryID,
            question = request.questionText,
            pillar_id = request.pillarID 
        )

        return ChatResponse (
            success=True,
            message="Response fetched successfully",
            result=result
        )
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/country", response_model=ChatResponse)
async def ask(request: ChatCountryRequest):
    """
    Chat endpoint:
    - Accepts user question in body
    - Runs RAG pipeline
    - Returns AI-generated answer
    """
    try:
        result = await chat_service.answer_country_question (
            country_id = request.countryID,
            questionText = request.questionText,
            historyText = request.historyText,
            faqid = request.faqid,
            pillar_id = request.pillarID 
        )

        return ChatResponse (
            success=True,
            message="Response fetched successfully",
            result=result
        )
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/global", response_model = ChatResponse)
async def ask(request: ChatGlobalRequest):
    """
    Chat endpoint:
    - Accepts user question in body
    - Runs RAG pipeline
    - Returns AI-generated answer
    """
    try:
        result = await chat_service.answer_global_question (
            questionText = request.questionText,
            historyText = request.historyText, 
            faqid = request.faqid,
        )

        return ChatResponse(
            success=True,
            message="Response fetched successfully",
            result=result
        )
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/cross-comparision", response_model = ChatResponse)
async def ask(request: ChatCrossComparisionRequest):

    try:
        result = await chat_service.answer_crossComparision (
            questionText = request.questionText,
            countryIDs = request.countryIDs,
            historyText = request.historyText
        )

        return ChatResponse(
            success=True,
            message="Response fetched successfully",
            result=result
        )
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/executive-slides",response_model=ChatCountryExecutiveSlidesResponse)
async def ask_Country_executive_slides(request: ChatCountryExecutiveSlidesRequest):
    """
    Executive intelligence dashboard endpoint.

    Returns:
    - Daily performance
    - Weekly performance
    - Monthly performance
    - Combined risks
    - Early warnings
    """

    try:

        response = await chat_service.answer_Country_executive_slides(
            country_id=request.countryId
        )

        return ChatCountryExecutiveSlidesResponse(
            success=response["success"],
            message=response["message"],
            result=response["result"]
        )

    except Exception as e:

        logger.error(
            f"Error in executive slides API: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
