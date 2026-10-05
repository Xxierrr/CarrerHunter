"""
Profile Pydantic schemas for request/response validation.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    """Update user profile — all fields optional."""
    name: str | None = None
    phone: str | None = None
    country: str | None = None
    city: str | None = None
    university: str | None = None
    degree: str | None = None
    degree_level: str | None = None
    major: str | None = None
    current_year: int | None = None
    current_semester: int | None = None
    graduation_date: date | None = None
    gpa: Decimal | None = None
    gpa_scale: Decimal | None = None
    work_authorization: dict | None = None
    remote_preference: str | None = None
    preferred_countries: list[str] | None = None
    preferred_cities: list[str] | None = None
    preferred_domains: list[str] | None = None
    preferred_companies: list[str] | None = None
    target_roles: list[str] | None = None
    min_duration_weeks: int | None = None
    max_duration_weeks: int | None = None
    preferred_start_date: date | None = None
    preferred_end_date: date | None = None
    portfolio_url: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    other_links: dict | None = None


class ProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str | None = None
    phone: str | None = None
    country: str | None = None
    city: str | None = None
    university: str | None = None
    degree: str | None = None
    degree_level: str | None = None
    major: str | None = None
    current_year: int | None = None
    current_semester: int | None = None
    graduation_date: date | None = None
    gpa: Decimal | None = None
    gpa_scale: Decimal | None = None
    work_authorization: dict | None = None
    remote_preference: str | None = None
    preferred_countries: list[str] | None = None
    preferred_cities: list[str] | None = None
    preferred_domains: list[str] | None = None
    preferred_companies: list[str] | None = None
    target_roles: list[str] | None = None
    min_duration_weeks: int | None = None
    max_duration_weeks: int | None = None
    preferred_start_date: date | None = None
    preferred_end_date: date | None = None
    portfolio_url: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    other_links: dict | None = None
    skills: list["SkillResponse"] = []
    experiences: list["ExperienceResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: str | None = None
    proficiency: str | None = None


class SkillResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str | None = None
    proficiency: str | None = None

    model_config = {"from_attributes": True}


class SkillsUpdate(BaseModel):
    skills: list[SkillCreate]


class ExperienceCreate(BaseModel):
    type: str = Field(pattern="^(project|internship|work|certification)$")
    title: str = Field(min_length=1, max_length=255)
    organization: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False
    url: str | None = None


class ExperienceUpdate(BaseModel):
    type: str | None = None
    title: str | None = None
    organization: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    url: str | None = None


class ExperienceResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str | None = None
    organization: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool
    url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
