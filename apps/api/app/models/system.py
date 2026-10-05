"""
System models: Eligibility, Match Scores, Crawl Runs, AI tracking.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.compat import GUID, JSONType


class EligibilityResult(Base):
    __tablename__ = "eligibility_results"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE")
    )
    internship_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("internships.id", ondelete="CASCADE")
    )
    overall_status: Mapped[str | None] = mapped_column(String(30))
    criteria: Mapped[dict | None] = mapped_column(JSONType())
    deterministic_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ai_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ai_explanation: Mapped[str | None] = mapped_column(Text)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class MatchScore(Base):
    __tablename__ = "match_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE")
    )
    internship_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("internships.id", ondelete="CASCADE")
    )
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    skill_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    education_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    location_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    experience_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    preference_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    breakdown: Mapped[dict | None] = mapped_column(JSONType())
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CrawlRun(Base):
    __tablename__ = "crawl_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("sources.id")
    )
    status: Mapped[str | None] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    jobs_new: Mapped[int] = mapped_column(Integer, default=0)
    jobs_updated: Mapped[int] = mapped_column(Integer, default=0)
    jobs_unchanged: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)

    # Relationships
    source: Mapped["Source"] = relationship(back_populates="crawl_runs")


class AIRequest(Base):
    __tablename__ = "ai_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    provider: Mapped[str] = mapped_column(String(50), default="gemini")
    model: Mapped[str | None] = mapped_column(String(100))
    request_type: Mapped[str | None] = mapped_column(String(50))
    input_hash: Mapped[str | None] = mapped_column(String(64))
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    cached: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str | None] = mapped_column(String(20))
    error: Mapped[str | None] = mapped_column(Text)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AICache(Base):
    __tablename__ = "ai_cache"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    input_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    request_type: Mapped[str | None] = mapped_column(String(50))
    model: Mapped[str | None] = mapped_column(String(100))
    result: Mapped[dict | None] = mapped_column(JSONType())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
