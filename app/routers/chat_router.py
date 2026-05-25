"""
Score analysis Router - API endpoints with database exception logging
Fire-and-forget pattern for long-running analysis tasks
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from app.view_models.ChatRequest import ChatCountryExecutiveSlidesRequest, ChatCountryExecutiveSlidesResponse, ChatCountryRequest, ChatCrossComparisionRequest, ChatGlobalRequest, ChatRequest
from app.view_models.AnalysisRequest import ChatResponse
from app.view_models.EmergingTrendsResult import ChatEmergingTrendsResponse
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


@router.get(
    "/emerging-trends-and-issues",
    response_model=ChatEmergingTrendsResponse,
    summary="Global emerging trends and issues feed",
)
async def get_emerging_trends_and_issues(
    countryCount: int = Query(
        default=8,
        ge=4,
        le=8,
        description="Number of country intelligence cards to return (4–8).",
    ),
):
    """
    Public homepage feed for emerging global risks and stability trends.

    Returns structured country cards suitable for a public-facing UI.
    """
    try:
        response = await chat_service.get_emerging_trends_and_issues(
            country_count=countryCount
        )

        if not response.get("success"):
            raise HTTPException(
                status_code=502,
                detail=response.get("message", "Failed to generate emerging trends"),
            )

        return ChatEmergingTrendsResponse(
            success=True,
            message=response["message"],
            result=response["result"],
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Error in emerging trends API: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))
