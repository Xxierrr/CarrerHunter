"""
Gemini AI Provider — concrete implementation of AIProvider.
Uses google-genai SDK with structured JSON output, caching, and rate limiting.
"""

import json
import time
import logging
from datetime import datetime, timezone
from typing import Any

from google import genai
from google.genai import types
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.services.ai.provider import AIProvider
from app.services.ai.schemas import ExtractedRequirements, RoleClassification, ResumeExtraction
from app.services.ai.prompts import (
    EXTRACT_REQUIREMENTS_PROMPT,
    CLASSIFY_ROLE_PROMPT,
    EXPLAIN_ELIGIBILITY_PROMPT,
    GENERATE_COVER_LETTER_PROMPT,
    PARSE_RESUME_PROMPT,
)
from app.services.ai.cache import AICache, generate_cache_key
from app.services.ai.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)
settings = get_settings()


class GeminiProvider(AIProvider):
    """Gemini AI provider with caching, rate limiting, and structured output."""

    def __init__(self, db_session_factory=None):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.client = None
        self.cache = AICache()
        self.rate_limiter = RateLimiter(
            rpm_limit=settings.gemini_rpm_limit,
            daily_limit=settings.gemini_daily_limit,
        )
        self._db_session_factory = db_session_factory

        # Initialize client only if API key is configured
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

    async def _call_gemini(
        self,
        prompt: str,
        request_type: str,
        response_schema: type | None = None,
        db: AsyncSession | None = None,
        cache_key: str | None = None,
    ) -> dict | str | None:
        """
        Core method to call Gemini with caching, rate limiting, and validation.
        """
        if not self.client:
            logger.warning("Gemini client not initialized. AI features unavailable.")
            return None

        # Check cache first
        if cache_key and db:
            cached = await self.cache.get(db, cache_key)
            if cached is not None:
                logger.info(f"Cache hit for {request_type}: {cache_key[:16]}...")
                await self._log_request(db, request_type, cache_key, cached=True)
                return cached

        # Check rate limits
        if not await self.rate_limiter.acquire():
            logger.warning(f"Rate limit reached for {request_type}. Skipping.")
            if db:
                await self._log_request(
                    db, request_type, cache_key, status="rate_limited"
                )
            return None

        # Make the API call
        start_time = time.monotonic()
        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,  # Low temperature for consistent extraction
            )

            if response_schema:
                config.response_schema = response_schema

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            latency_ms = int((time.monotonic() - start_time) * 1000)
            self.rate_limiter.record_success()

            # Parse response
            result_text = response.text
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from Gemini for {request_type}")
                if db:
                    await self._log_request(
                        db, request_type, cache_key,
                        status="failed", error="Invalid JSON response",
                        latency_ms=latency_ms,
                    )
                return None

            # Cache the result
            if cache_key and db:
                await self.cache.set(db, cache_key, request_type, self.model, result)

            # Log the request
            if db:
                input_tokens = getattr(response, 'usage_metadata', None)
                await self._log_request(
                    db, request_type, cache_key,
                    status="success", latency_ms=latency_ms,
                    input_tokens=getattr(input_tokens, 'prompt_token_count', None) if input_tokens else None,
                    output_tokens=getattr(input_tokens, 'candidates_token_count', None) if input_tokens else None,
                )

            return result

        except Exception as e:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            self.rate_limiter.record_failure(is_rate_limit="429" in str(e) or "quota" in str(e).lower())
            logger.error(f"Gemini API error for {request_type}: {e}")

            if db:
                await self._log_request(
                    db, request_type, cache_key,
                    status="failed", error=str(e), latency_ms=latency_ms,
                )

            # Exponential backoff for retries
            await self.rate_limiter.backoff_wait()
            return None

    async def _log_request(
        self,
        db: AsyncSession,
        request_type: str,
        input_hash: str | None = None,
        cached: bool = False,
        status: str = "success",
        error: str | None = None,
        latency_ms: int | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ):
        """Log AI request to database for monitoring."""
        from app.models.system import AIRequest

        log = AIRequest(
            provider="gemini",
            model=self.model,
            request_type=request_type,
            input_hash=input_hash,
            cached=cached,
            status=status,
            error=error,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        db.add(log)

    async def extract_requirements(
        self, job_description: str, job_title: str, db: AsyncSession | None = None
    ) -> dict:
        """Extract structured requirements from a job description."""
        cache_key = generate_cache_key(
            "extract_requirements",
            title=job_title,
            description=job_description[:2000],  # Limit for cache key stability
        )

        prompt = EXTRACT_REQUIREMENTS_PROMPT.format(
            title=job_title,
            description=job_description[:4000],  # Limit input size for token efficiency
        )

        result = await self._call_gemini(
            prompt=prompt,
            request_type="extract_requirements",
            response_schema=ExtractedRequirements,
            db=db,
            cache_key=cache_key,
        )

        if result is None:
            return ExtractedRequirements().model_dump()

        # Validate with Pydantic
        try:
            validated = ExtractedRequirements.model_validate(result)
            return validated.model_dump()
        except ValidationError as e:
            logger.error(f"Validation error for extracted requirements: {e}")
            return ExtractedRequirements().model_dump()

    async def classify_role(
        self, title: str, description: str, db: AsyncSession | None = None
    ) -> dict:
        """Classify an internship role."""
        cache_key = generate_cache_key(
            "classify_role",
            title=title,
            description=description[:500],
        )

        prompt = CLASSIFY_ROLE_PROMPT.format(
            title=title,
            description=description[:500] if description else "No description provided",
        )

        result = await self._call_gemini(
            prompt=prompt,
            request_type="classify_role",
            response_schema=RoleClassification,
            db=db,
            cache_key=cache_key,
        )

        if result is None:
            return RoleClassification(category="other").model_dump()

        try:
            validated = RoleClassification.model_validate(result)
            return validated.model_dump()
        except ValidationError:
            return RoleClassification(category="other").model_dump()

    async def explain_eligibility(
        self,
        candidate_summary: dict,
        job_summary: dict,
        criteria: list[dict],
        db: AsyncSession | None = None,
    ) -> str:
        """Generate eligibility explanation."""
        cache_key = generate_cache_key(
            "explain_eligibility",
            candidate=str(candidate_summary),
            job=str(job_summary),
        )

        prompt = EXPLAIN_ELIGIBILITY_PROMPT.format(
            candidate_summary=json.dumps(candidate_summary, indent=2),
            job_summary=json.dumps(job_summary, indent=2),
            criteria=json.dumps(criteria, indent=2),
        )

        result = await self._call_gemini(
            prompt=prompt,
            request_type="explain_eligibility",
            db=db,
            cache_key=cache_key,
        )

        if result is None:
            return "AI eligibility explanation is temporarily unavailable. Please review the criteria above."

        if isinstance(result, dict):
            return result.get("explanation", str(result))
        return str(result)

    async def generate_cover_letter(
        self,
        candidate_summary: dict,
        job_summary: dict,
        db: AsyncSession | None = None,
    ) -> str:
        """Generate a cover letter from verified candidate info only."""
        # No caching for cover letters (user may want variety)
        prompt = GENERATE_COVER_LETTER_PROMPT.format(
            candidate_summary=json.dumps(candidate_summary, indent=2),
            job_summary=json.dumps(job_summary, indent=2),
        )

        result = await self._call_gemini(
            prompt=prompt,
            request_type="generate_cover_letter",
            db=db,
        )

        if result is None:
            return "Cover letter generation is temporarily unavailable. Please try again later."

        if isinstance(result, dict):
            return result.get("cover_letter", str(result))
        return str(result)

    async def parse_resume_text(
        self, resume_text: str, db: AsyncSession | None = None
    ) -> dict:
        """Extract structured information from resume text."""
        cache_key = generate_cache_key(
            "parse_resume",
            text=resume_text[:3000],
        )

        prompt = PARSE_RESUME_PROMPT.format(
            resume_text=resume_text[:5000],
        )

        result = await self._call_gemini(
            prompt=prompt,
            request_type="parse_resume",
            response_schema=ResumeExtraction,
            db=db,
            cache_key=cache_key,
        )

        if result is None:
            return ResumeExtraction().model_dump()

        try:
            validated = ResumeExtraction.model_validate(result)
            return validated.model_dump()
        except ValidationError:
            return ResumeExtraction().model_dump()

    async def get_usage_stats(self) -> dict:
        """Return current usage statistics."""
        return {
            "provider": "gemini",
            "model": self.model,
            "rate_limiter": self.rate_limiter.get_stats(),
            "client_initialized": self.client is not None,
        }

    async def is_available(self) -> bool:
        """Check if Gemini is currently available."""
        return self.client is not None and self.rate_limiter.is_available


# Singleton instance
_gemini_provider: GeminiProvider | None = None


def get_ai_provider() -> GeminiProvider:
    """Get or create the singleton Gemini provider."""
    global _gemini_provider
    if _gemini_provider is None:
        _gemini_provider = GeminiProvider()
    return _gemini_provider
