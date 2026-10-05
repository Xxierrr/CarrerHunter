"""
AI API routes — endpoints for AI-powered features.
All AI calls go through the provider abstraction with caching and rate limiting.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession
from app.services.ai.gemini import get_ai_provider

router = APIRouter()


class AnalyzeJobRequest(BaseModel):
    title: str
    description: str


class CoverLetterRequest(BaseModel):
    internship_id: str
    custom_instructions: str | None = None


@router.post("/analyze-job")
async def analyze_job(
    request: AnalyzeJobRequest, current_user: CurrentUser, db: DbSession
):
    """Extract structured requirements from a job description using AI."""
    provider = get_ai_provider()

    if not await provider.is_available():
        return {
            "status": "unavailable",
            "message": "AI analysis temporarily unavailable. Daily quota may be reached.",
            "requirements": None,
        }

    requirements = await provider.extract_requirements(
        request.description, request.title, db=db
    )

    return {
        "status": "success",
        "requirements": requirements,
    }


@router.get("/usage")
async def get_ai_usage(current_user: CurrentUser):
    """Get current AI usage statistics."""
    provider = get_ai_provider()
    stats = await provider.get_usage_stats()
    return stats
