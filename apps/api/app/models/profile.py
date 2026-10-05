"""
User Profile, Skills, Experience, and Resume models.
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


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    university: Mapped[str | None] = mapped_column(String(255))
    degree: Mapped[str | None] = mapped_column(String(100))
    degree_level: Mapped[str | None] = mapped_column(String(50))
    major: Mapped[str | None] = mapped_column(String(255))
    current_year: Mapped[int | None] = mapped_column(Integer)
    current_semester: Mapped[int | None] = mapped_column(Integer)
    graduation_date: Mapped[date | None] = mapped_column(Date)
    gpa: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    gpa_scale: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=10.0)
    work_authorization: Mapped[dict | None] = mapped_column(JSONType())
    remote_preference: Mapped[str | None] = mapped_column(String(20))
    preferred_countries: Mapped[list[str] | None] = mapped_column(ArrayType(Text))
    preferred_cities: Mapped[list[str] | None] = mapped_column(ArrayType(Text))
    preferred_domains: Mapped[list[str] | None] = mapped_column(ArrayType(Text))
    preferred_companies: Mapped[list[str] | None] = mapped_column(ArrayType(Text))
    target_roles: Mapped[list[str] | None] = mapped_column(ArrayType(Text))
    min_duration_weeks: Mapped[int | None] = mapped_column(Integer)
    max_duration_weeks: Mapped[int | None] = mapped_column(Integer)
    preferred_start_date: Mapped[date | None] = mapped_column(Date)
    preferred_end_date: Mapped[date | None] = mapped_column(Date)
    portfolio_url: Mapped[str | None] = mapped_column(Text)
    github_url: Mapped[str | None] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    other_links: Mapped[dict | None] = mapped_column(JSONType())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="profile")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))
    normalized_name: Mapped[str | None] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserSkill(Base):
    __tablename__ = "user_skills"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    proficiency: Mapped[str | None] = mapped_column(String(20))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship()


class UserExperience(Base):
    __tablename__ = "user_experiences"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE")
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    organization: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    technologies: Mapped[list[str] | None] = mapped_column(ArrayType(Text))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="experiences")


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE")
    )
    filename: Mapped[str | None] = mapped_column(String(255))
    file_path: Mapped[str | None] = mapped_column(Text)
    file_type: Mapped[str | None] = mapped_column(String(20))
    file_size: Mapped[int | None] = mapped_column(Integer)
    extracted_data: Mapped[dict | None] = mapped_column(JSONType())
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="resumes")
