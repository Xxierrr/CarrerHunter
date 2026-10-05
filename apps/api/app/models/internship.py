"""
Internship, Company, Source, and related models.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.compat import GUID, JSONType, ArrayType


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    website: Mapped[str | None] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(String(100))
    size: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    internships: Mapped[list["Internship"]] = relationship(back_populates="company")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50))
    base_url: Mapped[str | None] = mapped_column(Text)
    adapter_name: Mapped[str | None] = mapped_column(String(100))
    crawl_frequency_minutes: Mapped[int] = mapped_column(Integer, default=360)
    robots_policy: Mapped[str | None] = mapped_column(String(50))
    automation_status: Mapped[str] = mapped_column(String(30), default="supported")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    config: Mapped[dict | None] = mapped_column(JSONType())
    last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    jobs_found_total: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    internships: Mapped[list["Internship"]] = relationship(back_populates="source")
    crawl_runs: Mapped[list["CrawlRun"]] = relationship(back_populates="source")


class Internship(Base):
    __tablename__ = "internships"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("sources.id")
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("companies.id")
    )
    source_job_id: Mapped[str | None] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    country: Mapped[str | None] = mapped_column(String(100), index=True)
    remote_status: Mapped[str | None] = mapped_column(String(20), index=True)
    employment_type: Mapped[str | None] = mapped_column(String(50))
    duration_weeks: Mapped[int | None] = mapped_column(Integer)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    application_deadline: Mapped[date | None] = mapped_column(Date, index=True)
    salary_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    salary_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    salary_currency: Mapped[str | None] = mapped_column(String(10))
    salary_period: Mapped[str | None] = mapped_column(String(20))
    degree_requirements: Mapped[dict | None] = mapped_column(JSONType())
    field_requirements: Mapped[list[str] | None] = mapped_column(ArrayType(Text))
    graduation_requirements: Mapped[dict | None] = mapped_column(JSONType())
    gpa_requirement: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    experience_requirement: Mapped[dict | None] = mapped_column(JSONType())
    work_authorization: Mapped[dict | None] = mapped_column(JSONType())
    visa_sponsorship: Mapped[bool | None] = mapped_column(Boolean)
    application_url: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    raw_content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    source: Mapped["Source"] = relationship(back_populates="internships")
    company: Mapped["Company"] = relationship(back_populates="internships")
    skills: Mapped[list["InternshipSkill"]] = relationship(
        back_populates="internship", cascade="all, delete-orphan"
    )


class InternshipSkill(Base):
    __tablename__ = "internship_skills"

    internship_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("internships.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    internship: Mapped["Internship"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship()
