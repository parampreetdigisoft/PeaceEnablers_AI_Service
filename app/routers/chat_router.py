"""
Score analysis Router - API endpoints with database exception logging
Fire-and-forget pattern for long-running analysis tasks
"""
import logging
from fastapi import APIRouter, HTTPException
from app.view_models.ChatRequest import ChatRequest
from app.view_models.AnalysisRequest import AnalysisResponse, ChatResponse
logger = logging.getLogger(__name__)
from app.services.rag_query_service import rag_query_service


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
        result = await rag_query_service.answer_country_question (
            country_id = request.countryID,
            question = request.questionText,
            pillar_id = request.pillarID 
        )

        return ChatResponse(
            success=True,
            message="Response fetched successfully",
            result=result
        )
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
