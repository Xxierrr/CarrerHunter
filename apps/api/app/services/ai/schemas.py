"""
Pydantic schemas for structured AI output validation.
These schemas ensure Gemini responses are validated, not trusted blindly.
"""

from pydantic import BaseModel, Field


class DegreeRequirement(BaseModel):
    required: bool = False
    level: str | None = None  # bachelors, masters, phd, any
    fields: list[str] = Field(default_factory=list)
    source_text: str | None = None


class GraduationRequirement(BaseModel):
    minimum_year: int | None = None
    maximum_year: int | None = None
    must_be_enrolled: bool | None = None
    source_text: str | None = None


class ExperienceRequirement(BaseModel):
    required: bool = False
    minimum_years: float | None = None
    type: str | None = None  # professional, internship, academic, any
    details: str | None = None
    source_text: str | None = None


class WorkAuthorizationRequirement(BaseModel):
    required: bool = False
    countries: list[str] = Field(default_factory=list)
    visa_sponsorship: bool | None = None
    details: str | None = None
    source_text: str | None = None


class ExtractedRequirements(BaseModel):
    """Structured output from AI requirement extraction."""
    role_title: str | None = None
    role_category: str | None = None  # software_engineering, data_science, product, design, etc.
    skills_required: list[str] = Field(default_factory=list)
    skills_preferred: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    degree: DegreeRequirement = Field(default_factory=DegreeRequirement)
    graduation: GraduationRequirement = Field(default_factory=GraduationRequirement)
    experience: ExperienceRequirement = Field(default_factory=ExperienceRequirement)
    work_authorization: WorkAuthorizationRequirement = Field(
        default_factory=WorkAuthorizationRequirement
    )
    gpa_minimum: float | None = None
    remote_status: str | None = None  # remote, hybrid, onsite, unknown
    duration_weeks: int | None = None
    location: str | None = None
    country: str | None = None
    salary_info: str | None = None
    application_deadline: str | None = None
    key_responsibilities: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class RoleClassification(BaseModel):
    """Structured output from role classification."""
    category: str  # software_engineering, data_science, ml_ai, product, design, marketing, finance, research, other
    subcategory: str | None = None
    seniority: str = "intern"  # intern, junior, mid, senior
    domain: str | None = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ResumeExtraction(BaseModel):
    """Structured output from resume parsing."""
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    education: list[dict] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    links: dict = Field(default_factory=dict)
