# api.py
from fastapi import APIRouter, Depends, Request
from datetime import datetime, timezone
from .import services, models, dependencies

router = APIRouter()

@router.post("/analyze", response_model=models.AnalysisResponse)
async def analyze_website(
    request: models.AnalysisRequest,
    api_key: str = Depends(dependencies.get_api_key)
):
    """
    Initiates web scraping and AI-driven analysis of a given website homepage.
    """
    # services.get_website_analysis now returns a models.AnalysisResponse object
    analysis_data = await services.get_website_analysis(str(request.url), request.questions)

    # Access attributes directly from the Pydantic model
    return models.AnalysisResponse(
        company_info=analysis_data.company_info,
        extracted_answers=analysis_data.extracted_answers
    )

@router.post("/chat", response_model=models.ChatResponse)
async def conversational_chat(
    request: models.ChatRequest,
    api_key: str = Depends(dependencies.get_api_key)
):
    """
    Enables conversational follow-up questions about a previously analyzed website.
    """
    agent_response = await services.get_conversational_answer(
        url=str(request.url),
        query=request.query,
        history=request.conversation_history
    )
    
    return models.ChatResponse(
        agent_response=agent_response.get("agent_response"),
        context_sources=agent_response.get("context_sources", [])
    )