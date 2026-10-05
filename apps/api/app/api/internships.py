"""
Internship API routes: search, list, detail, save/unsave, recommendations.
"""

import uuid
from math import ceil

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models.internship import Internship, Company, InternshipSkill
from app.models.profile import Skill
from app.models.application import SavedInternship
from app.models.system import EligibilityResult, MatchScore
from app.schemas.internship import (
    InternshipResponse,
    InternshipDetailResponse,
    PaginatedResponse,
)

router = APIRouter()


def _build_internship_response(
    internship: Internship,
    company: Company | None,
    skills: list[str],
    eligibility_status: str | None = None,
    match_score: float | None = None,
    is_saved: bool = False,
) -> InternshipResponse:
    """Build standardized internship response."""
    return InternshipResponse(
        id=internship.id,
        company_name=company.name if company else None,
        company_logo=company.logo_url if company else None,
        title=internship.title,
        description=internship.description[:500] if internship.description else None,
        location=internship.location,
        country=internship.country,
        remote_status=internship.remote_status,
        employment_type=internship.employment_type,
        duration_weeks=internship.duration_weeks,
        start_date=internship.start_date,
        end_date=internship.end_date,
        application_deadline=internship.application_deadline,
        salary_min=internship.salary_min,
        salary_max=internship.salary_max,
        salary_currency=internship.salary_currency,
        salary_period=internship.salary_period,
        skills=skills,
        application_url=internship.application_url,
        source_url=internship.source_url,
        posted_at=internship.posted_at,
        status=internship.status,
        first_seen_at=internship.first_seen_at,
        last_seen_at=internship.last_seen_at,
        eligibility_status=eligibility_status,
        match_score=match_score,
        is_saved=is_saved,
    )


@router.get("", response_model=PaginatedResponse)
async def list_internships(
    current_user: CurrentUser,
    db: DbSession,
    q: str | None = None,
    company: str | None = None,
    country: str | None = None,
    remote: bool | None = None,
    min_match: float | None = None,
    eligibility: str | None = None,
    posted_after: str | None = None,
    deadline_before: str | None = None,
    sort: str = "posted_at",
    order: str = "desc",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Search and filter internships with pagination."""
    query = select(Internship).where(Internship.status == "active")

    # Text search (ILIKE for cross-database compatibility)
    if q:
        q_stripped = q.strip()
        if len(q_stripped) >= 2:
            query = query.where(
                or_(
                    Internship.title.ilike(f"%{q_stripped}%"),
                    Internship.description.ilike(f"%{q_stripped}%"),
                    Internship.location.ilike(f"%{q_stripped}%"),
                )
            )

    # Filters
    if company:
        query = query.join(Company).where(Company.name.ilike(f"%{company}%"))

    if country:
        query = query.where(Internship.country.ilike(f"%{country}%"))

    if remote is not None:
        if remote:
            query = query.where(Internship.remote_status == "remote")
        else:
            query = query.where(Internship.remote_status != "remote")

    if posted_after:
        query = query.where(Internship.posted_at >= posted_after)

    if deadline_before:
        query = query.where(Internship.application_deadline <= deadline_before)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sorting
    sort_column = getattr(Internship, sort, Internship.posted_at)
    order_func = desc if order == "desc" else asc
    query = query.order_by(order_func(sort_column).nullslast())

    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    internships = result.scalars().all()

    # Build responses with company info, skills, eligibility, and saved status
    items = []
    for internship in internships:
        # Load company
        company_obj = None
        if internship.company_id:
            comp_result = await db.execute(
                select(Company).where(Company.id == internship.company_id)
            )
            company_obj = comp_result.scalar_one_or_none()

        # Load skills
        skills_result = await db.execute(
            select(Skill.name)
            .join(InternshipSkill, InternshipSkill.skill_id == Skill.id)
            .where(InternshipSkill.internship_id == internship.id)
        )
        skill_names = [row[0] for row in skills_result.all()]

        # Check saved status
        saved_result = await db.execute(
            select(SavedInternship).where(
                SavedInternship.user_id == current_user.id,
                SavedInternship.internship_id == internship.id,
            )
        )
        is_saved = saved_result.scalar_one_or_none() is not None

        # Get eligibility
        elig_result = await db.execute(
            select(EligibilityResult).where(
                EligibilityResult.user_id == current_user.id,
                EligibilityResult.internship_id == internship.id,
            )
        )
        elig = elig_result.scalar_one_or_none()

        # Get match score
        match_result = await db.execute(
            select(MatchScore).where(
                MatchScore.user_id == current_user.id,
                MatchScore.internship_id == internship.id,
            )
        )
        match = match_result.scalar_one_or_none()

        items.append(
            _build_internship_response(
                internship=internship,
                company=company_obj,
                skills=skill_names,
                eligibility_status=elig.overall_status if elig else None,
                match_score=float(match.overall_score) if match and match.overall_score else None,
                is_saved=is_saved,
            )
        )

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=ceil(total / limit) if limit > 0 else 0,
    )


# NOTE: These fixed-path routes MUST be defined BEFORE the /{internship_id} route
# otherwise FastAPI treats "saved", "recommendations" as a UUID and returns 422

@router.get("/saved/list", response_model=list[InternshipResponse])
async def get_saved_internships(current_user: CurrentUser, db: DbSession):
    """Get all saved internships."""
    result = await db.execute(
        select(SavedInternship)
        .where(SavedInternship.user_id == current_user.id)
        .order_by(SavedInternship.saved_at.desc())
    )
    saved_list = result.scalars().all()

    items = []
    for saved in saved_list:
        intern_result = await db.execute(
            select(Internship).where(Internship.id == saved.internship_id)
        )
        internship = intern_result.scalar_one_or_none()
        if not internship:
            continue

        company = None
        if internship.company_id:
            comp_result = await db.execute(
                select(Company).where(Company.id == internship.company_id)
            )
            company = comp_result.scalar_one_or_none()

        skills_result = await db.execute(
            select(Skill.name)
            .join(InternshipSkill, InternshipSkill.skill_id == Skill.id)
            .where(InternshipSkill.internship_id == internship.id)
        )
        skill_names = [row[0] for row in skills_result.all()]

        items.append(
            _build_internship_response(
                internship=internship,
                company=company,
                skills=skill_names,
                is_saved=True,
            )
        )

    return items


@router.get("/recommendations")
async def get_internship_recommendations(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get personalized internship recommendations based on user profile."""
    from app.services.recommendations import get_recommendations

    recommendations = await get_recommendations(
        db=db,
        user_id=str(current_user.id),
        limit=limit,
    )
    return recommendations


# Parameterized routes AFTER fixed-path routes
@router.get("/{internship_id}", response_model=InternshipDetailResponse)
async def get_internship(
    internship_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """Get full internship details with eligibility and match info."""
    result = await db.execute(
        select(Internship).where(Internship.id == internship_id)
    )
    internship = result.scalar_one_or_none()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    # Load company
    company = None
    if internship.company_id:
        comp_result = await db.execute(
            select(Company).where(Company.id == internship.company_id)
        )
        company = comp_result.scalar_one_or_none()

    # Load skills
    skills_result = await db.execute(
        select(Skill.name)
        .join(InternshipSkill, InternshipSkill.skill_id == Skill.id)
        .where(InternshipSkill.internship_id == internship.id)
    )
    skill_names = [row[0] for row in skills_result.all()]

    # Check saved
    saved_result = await db.execute(
        select(SavedInternship).where(
            SavedInternship.user_id == current_user.id,
            SavedInternship.internship_id == internship.id,
        )
    )
    is_saved = saved_result.scalar_one_or_none() is not None

    # Eligibility
    elig_result = await db.execute(
        select(EligibilityResult).where(
            EligibilityResult.user_id == current_user.id,
            EligibilityResult.internship_id == internship.id,
        )
    )
    elig = elig_result.scalar_one_or_none()

    # Match
    match_result = await db.execute(
        select(MatchScore).where(
            MatchScore.user_id == current_user.id,
            MatchScore.internship_id == internship.id,
        )
    )
    match = match_result.scalar_one_or_none()

    return InternshipDetailResponse(
        id=internship.id,
        company_name=company.name if company else None,
        company_logo=company.logo_url if company else None,
        title=internship.title,
        description=internship.description,
        location=internship.location,
        country=internship.country,
        remote_status=internship.remote_status,
        employment_type=internship.employment_type,
        duration_weeks=internship.duration_weeks,
        start_date=internship.start_date,
        end_date=internship.end_date,
        application_deadline=internship.application_deadline,
        salary_min=internship.salary_min,
        salary_max=internship.salary_max,
        salary_currency=internship.salary_currency,
        salary_period=internship.salary_period,
        skills=skill_names,
        application_url=internship.application_url,
        source_url=internship.source_url,
        posted_at=internship.posted_at,
        status=internship.status,
        first_seen_at=internship.first_seen_at,
        last_seen_at=internship.last_seen_at,
        eligibility_status=elig.overall_status if elig else None,
        match_score=float(match.overall_score) if match and match.overall_score else None,
        is_saved=is_saved,
        degree_requirements=internship.degree_requirements,
        field_requirements=internship.field_requirements,
        graduation_requirements=internship.graduation_requirements,
        gpa_requirement=internship.gpa_requirement,
        experience_requirement=internship.experience_requirement,
        work_authorization=internship.work_authorization,
        visa_sponsorship=internship.visa_sponsorship,
        eligibility_criteria=elig.criteria if elig else None,
        eligibility_explanation=elig.ai_explanation if elig else None,
        match_breakdown=match.breakdown if match else None,
    )


@router.post("/{internship_id}/save", status_code=201)
async def save_internship(
    internship_id: uuid.UUID, current_user: CurrentUser, db: DbSession
):
    """Save an internship."""
    # Verify internship exists
    result = await db.execute(
        select(Internship).where(Internship.id == internship_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Internship not found")

    # Check if already saved
    existing = await db.execute(
        select(SavedInternship).where(
            SavedInternship.user_id == current_user.id,
            SavedInternship.internship_id == internship_id,
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Already saved"}

    saved = SavedInternship(user_id=current_user.id, internship_id=internship_id)
    db.add(saved)
    return {"message": "Internship saved"}


@router.delete("/{internship_id}/save", status_code=204)
async def unsave_internship(
    internship_id: uuid.UUID, current_user: CurrentUser, db: DbSession
):
    """Remove an internship from saved list."""
    result = await db.execute(
        select(SavedInternship).where(
            SavedInternship.user_id == current_user.id,
            SavedInternship.internship_id == internship_id,
        )
    )
    saved = result.scalar_one_or_none()
    if saved:
        await db.delete(saved)
