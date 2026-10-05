"""
AI response caching — essential for free-tier Gemini usage.
Check cache before every Gemini call.
"""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


def generate_cache_key(request_type: str, **kwargs) -> str:
    """Generate a deterministic SHA-256 hash for cache lookup."""
    # Sort keys for deterministic hashing
    payload = json.dumps({"type": request_type, **kwargs}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


class AICache:
    """AI response cache using PostgreSQL (with optional Redis layer)."""

    # Default TTLs per request type
    DEFAULT_TTLS = {
        "extract_requirements": timedelta(days=30),
        "classify_role": timedelta(days=30),
        "explain_eligibility": timedelta(days=7),
        "generate_cover_letter": timedelta(days=1),
        "parse_resume": timedelta(days=30),
    }

    async def get(self, db: AsyncSession, cache_key: str) -> dict | None:
        """Check cache for a previous result. Returns None on miss."""
        from app.models.system import AICache as AICacheModel

        result = await db.execute(
            select(AICacheModel).where(
                AICacheModel.input_hash == cache_key,
                # Only return non-expired entries
                (AICacheModel.expires_at.is_(None)) | (AICacheModel.expires_at > datetime.now(timezone.utc)),
            )
        )
        cached = result.scalar_one_or_none()
        if cached and cached.result:
            return cached.result
        return None

    async def set(
        self,
        db: AsyncSession,
        cache_key: str,
        request_type: str,
        model: str,
        result: dict,
        ttl: timedelta | None = None,
    ) -> None:
        """Store a result in the cache."""
        from app.models.system import AICache as AICacheModel

        if ttl is None:
            ttl = self.DEFAULT_TTLS.get(request_type, timedelta(days=7))

        expires_at = datetime.now(timezone.utc) + ttl

        # Upsert
        existing = await db.execute(
            select(AICacheModel).where(AICacheModel.input_hash == cache_key)
        )
        cached = existing.scalar_one_or_none()

        if cached:
            cached.result = result
            cached.model = model
            cached.expires_at = expires_at
            cached.created_at = datetime.now(timezone.utc)
        else:
            entry = AICacheModel(
                input_hash=cache_key,
                request_type=request_type,
                model=model,
                result=result,
                expires_at=expires_at,
            )
            db.add(entry)

    async def cleanup_expired(self, db: AsyncSession) -> int:
        """Remove expired cache entries. Returns count of deleted entries."""
        from app.models.system import AICache as AICacheModel

        result = await db.execute(
            delete(AICacheModel).where(
                AICacheModel.expires_at.isnot(None),
                AICacheModel.expires_at < datetime.now(timezone.utc),
            )
        )
        return result.rowcount
