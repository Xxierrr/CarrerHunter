"""
Profile API routes: get/update profile, skills, experiences, resume upload.
"""

import os
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.config import get_settings
from app.models.profile import UserProfile, Skill, UserSkill, UserExperience, Resume
from app.schemas.profile import (
    ProfileUpdate,
    ProfileResponse,
    SkillCreate,
    SkillResponse,
    SkillsUpdate,
    ExperienceCreate,
    ExperienceUpdate,
    ExperienceResponse,
)

settings = get_settings()
router = APIRouter()


@router.get("", response_model=ProfileResponse)
async def get_profile(current_user: CurrentUser, db: DbSession):
    """Get the current user's profile with skills and experiences."""
    result = await db.execute(
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Load skills
    skills_result = await db.execute(
        select(UserSkill, Skill)
        .join(Skill, UserSkill.skill_id == Skill.id)
        .where(UserSkill.user_id == current_user.id)
    )
    skills = [
        SkillResponse(
            id=skill.id,
            name=skill.name,
            category=skill.category,
            proficiency=us.proficiency,
        )
        for us, skill in skills_result.all()
    ]

    # Load experiences
    exp_result = await db.execute(
        select(UserExperience)
        .where(UserExperience.user_id == current_user.id)
        .order_by(UserExperience.start_date.desc().nullslast())
    )
    experiences = [
        ExperienceResponse.model_validate(exp)
        for exp in exp_result.scalars().all()
    ]

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        name=profile.name,
        phone=profile.phone,
        country=profile.country,
        city=profile.city,
        university=profile.university,
        degree=profile.degree,
        degree_level=profile.degree_level,
        major=profile.major,
        current_year=profile.current_year,
        current_semester=profile.current_semester,
        graduation_date=profile.graduation_date,
        gpa=profile.gpa,
        gpa_scale=profile.gpa_scale,
        work_authorization=profile.work_authorization,
        remote_preference=profile.remote_preference,
        preferred_countries=profile.preferred_countries,
        preferred_cities=profile.preferred_cities,
        preferred_domains=profile.preferred_domains,
        preferred_companies=profile.preferred_companies,
        target_roles=profile.target_roles,
        min_duration_weeks=profile.min_duration_weeks,
        max_duration_weeks=profile.max_duration_weeks,
        preferred_start_date=profile.preferred_start_date,
        preferred_end_date=profile.preferred_end_date,
        portfolio_url=profile.portfolio_url,
        github_url=profile.github_url,
        linkedin_url=profile.linkedin_url,
        other_links=profile.other_links,
        skills=skills,
        experiences=experiences,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    updates: ProfileUpdate, current_user: CurrentUser, db: DbSession
):
    """Update the current user's profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update only provided fields
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.flush()
    await db.refresh(profile)

    # Return full profile (reuse GET logic)
    return await get_profile(current_user, db)


@router.put("/skills", response_model=list[SkillResponse])
async def update_skills(
    skills_update: SkillsUpdate, current_user: CurrentUser, db: DbSession
):
    """Replace user's skills with the provided list."""
    # Remove existing user skills
    await db.execute(
        delete(UserSkill).where(UserSkill.user_id == current_user.id)
    )

    result_skills = []
    for skill_data in skills_update.skills:
        # Find or create skill
        normalized = skill_data.name.lower().strip()
        result = await db.execute(
            select(Skill).where(Skill.normalized_name == normalized)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            skill = Skill(
                name=skill_data.name.strip(),
                category=skill_data.category,
                normalized_name=normalized,
            )
            db.add(skill)
            await db.flush()

        # Create user-skill link
        user_skill = UserSkill(
            user_id=current_user.id,
            skill_id=skill.id,
            proficiency=skill_data.proficiency,
        )
        db.add(user_skill)

        result_skills.append(
            SkillResponse(
                id=skill.id,
                name=skill.name,
                category=skill.category,
                proficiency=skill_data.proficiency,
            )
        )

    return result_skills


@router.post("/experiences", response_model=ExperienceResponse, status_code=201)
async def create_experience(
    experience: ExperienceCreate, current_user: CurrentUser, db: DbSession
):
    """Add a new experience entry."""
    exp = UserExperience(
        user_id=current_user.id,
        type=experience.type,
        title=experience.title,
        organization=experience.organization,
        description=experience.description,
        technologies=experience.technologies,
        start_date=experience.start_date,
        end_date=experience.end_date,
        is_current=experience.is_current,
        url=experience.url,
    )
    db.add(exp)
    await db.flush()
    await db.refresh(exp)
    return ExperienceResponse.model_validate(exp)


@router.put("/experiences/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    experience_id: uuid.UUID,
    updates: ExperienceUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Update an experience entry."""
    result = await db.execute(
        select(UserExperience).where(
            UserExperience.id == experience_id,
            UserExperience.user_id == current_user.id,
        )
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exp, field, value)

    await db.flush()
    await db.refresh(exp)
    return ExperienceResponse.model_validate(exp)


@router.delete("/experiences/{experience_id}", status_code=204)
async def delete_experience(
    experience_id: uuid.UUID, current_user: CurrentUser, db: DbSession
):
    """Delete an experience entry."""
    result = await db.execute(
        select(UserExperience).where(
            UserExperience.id == experience_id,
            UserExperience.user_id == current_user.id,
        )
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")

    await db.delete(exp)


@router.post("/resume/upload", status_code=201)
async def upload_resume(
    current_user: CurrentUser,
    db: DbSession,
    file: UploadFile = File(...),
):
    """Upload a resume (PDF or DOCX)."""
    # Validate file type
    allowed_types = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are accepted",
        )

    # Validate file size
    max_size = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb} MB",
        )

    # Save file
    upload_dir = os.path.join(settings.upload_dir, str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # Create resume record
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(content),
        is_primary=True,
    )

    # Mark other resumes as non-primary
    existing = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id, Resume.is_primary == True)
    )
    for existing_resume in existing.scalars().all():
        existing_resume.is_primary = False

    db.add(resume)
    await db.flush()

    return {
        "id": str(resume.id),
        "filename": resume.filename,
        "file_type": resume.file_type,
        "file_size": resume.file_size,
        "is_primary": resume.is_primary,
        "uploaded_at": resume.uploaded_at.isoformat(),
    }
