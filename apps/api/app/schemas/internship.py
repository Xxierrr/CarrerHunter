"""
Internship Pydantic schemas.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class InternshipResponse(BaseModel):
    id: uuid.UUID
    company_name: str | None = None
    company_logo: str | None = None
    title: str
    description: str | None = None
    location: str | None = None
    country: str | None = None
    remote_status: str | None = None
    employment_type: str | None = None
    duration_weeks: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    application_deadline: date | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    skills: list[str] = []
    application_url: str | None = None
    source_url: str | None = None
    posted_at: datetime | None = None
    status: str = "active"
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None

    # Eligibility & matching (populated per-user)
    eligibility_status: str | None = None
    match_score: float | None = None
    is_saved: bool = False

    model_config = {"from_attributes": True}


class InternshipDetailResponse(InternshipResponse):
    """Extended response with full details."""
    degree_requirements: dict | None = None
    field_requirements: list[str] | None = None
    graduation_requirements: dict | None = None
    gpa_requirement: Decimal | None = None
    experience_requirement: dict | None = None
    work_authorization: dict | None = None
    visa_sponsorship: bool | None = None
    raw_content: str | None = None

    # Eligibility detail
    eligibility_criteria: list[dict] | None = None
    eligibility_explanation: str | None = None

    # Match detail
    match_breakdown: dict | None = None


class InternshipSearchParams(BaseModel):
    q: str | None = None
    company: str | None = None
    country: str | None = None
    remote: bool | None = None
    min_match: float | None = None
    eligibility: str | None = None
    posted_after: date | None = None
    deadline_before: date | None = None
    skills: list[str] | None = None
    sort: str = "posted_at"
    order: str = "desc"
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: list[InternshipResponse]
    total: int
    page: int
    limit: int
    pages: int
