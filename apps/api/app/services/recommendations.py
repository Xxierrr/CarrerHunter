"""
Internship Recommendation Engine — Step 8.4

Generates personalized internship recommendations based on:
1. User skills overlap with internship required skills
2. Match scores (if computed)
3. Eligibility results
4. User preferences (location, remote, domain)
5. Recency of posting

Returns ranked list of recommendations with explanation.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, and_, func, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.profile import UserProfile, UserSkill, Skill
from app.models.internship import Internship, Company, InternshipSkill
from app.models.application import SavedInternship, Application
from app.models.system import MatchScore, EligibilityResult

logger = logging.getLogger(__name__)


async def get_recommendations(
    db: AsyncSession,
    user_id: str,
    limit: int = 10,
    exclude_saved: bool = True,
    exclude_applied: bool = True,
) -> list[dict]:
    """
    Generate personalized recommendations for a user.

    Strategy:
    1. First, use match scores if available (pre-computed)
    2. Fall back to skill-overlap heuristic for unscored internships
    3. Apply user preference filters
    4. Rank by composite score and recency
    """
    import uuid
    user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id

    # Load user profile
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_uuid)
    )
    profile = profile_result.scalar_one_or_none()

    # Load user skills
    skills_result = await db.execute(
        select(Skill.name, Skill.id)
        .join(UserSkill, UserSkill.skill_id == Skill.id)
        .where(UserSkill.user_id == user_uuid)
    )
    user_skills = {row[0].lower(): row[1] for row in skills_result.all()}
    user_skill_ids = set(user_skills.values())

    # Get IDs to exclude (already saved / applied)
    exclude_ids = set()

    if exclude_saved:
        saved_result = await db.execute(
            select(SavedInternship.internship_id).where(
                SavedInternship.user_id == user_uuid
            )
        )
        exclude_ids.update(row[0] for row in saved_result.all())

    if exclude_applied:
        applied_result = await db.execute(
            select(Application.internship_id).where(
                Application.user_id == user_uuid
            )
        )
        exclude_ids.update(row[0] for row in applied_result.all())

    # Strategy 1: Use pre-computed match scores
    scored_q = (
        select(MatchScore.internship_id, MatchScore.overall_score)
        .where(
            MatchScore.user_id == user_uuid,
            MatchScore.overall_score != None,
        )
        .order_by(desc(MatchScore.overall_score))
        .limit(limit * 3)  # Fetch extra to account for filtering
    )
    scored_result = await db.execute(scored_q)
    scored_ids = {row[0]: float(row[1]) for row in scored_result.all()}

    # Strategy 2: Skill-overlap heuristic for remaining internships
    # Find internships that share skills with the user
    if user_skill_ids:
        skill_overlap_q = (
            select(
                InternshipSkill.internship_id,
                func.count(InternshipSkill.skill_id).label("overlap_count"),
            )
            .where(InternshipSkill.skill_id.in_(user_skill_ids))
            .group_by(InternshipSkill.internship_id)
            .order_by(desc("overlap_count"))
            .limit(limit * 3)
        )
        overlap_result = await db.execute(skill_overlap_q)
        skill_overlaps = {row[0]: row[1] for row in overlap_result.all()}
    else:
        skill_overlaps = {}

    # Combine candidates
    candidate_ids = set(scored_ids.keys()) | set(skill_overlaps.keys())
    candidate_ids -= exclude_ids

    if not candidate_ids:
        # Fallback: return recent active internships
        fallback_q = (
            select(Internship)
            .where(
                Internship.status == "active",
                Internship.id.notin_(exclude_ids) if exclude_ids else True,
            )
            .order_by(desc(Internship.posted_at))
            .limit(limit)
        )
        result = await db.execute(fallback_q)
        internships = result.scalars().all()
        return await _build_recommendation_list(
            db, internships, user_uuid, {}, {}, "recent"
        )

    # Load actual internship records
    internships_q = (
        select(Internship)
        .where(
            Internship.id.in_(candidate_ids),
            Internship.status == "active",
        )
    )
    result = await db.execute(internships_q)
    internships = result.scalars().all()

    # Score and rank candidates
    ranked = []
    for internship in internships:
        iid = internship.id

        # Composite score: 60% match_score + 20% skill_overlap + 20% recency
        match_score = scored_ids.get(iid, 0)
        overlap_count = skill_overlaps.get(iid, 0)
        max_overlap = max(skill_overlaps.values()) if skill_overlaps else 1
        overlap_score = (overlap_count / max(max_overlap, 1)) * 100

        # Recency score: favor internships posted recently
        if internship.posted_at:
            days_old = (datetime.now(timezone.utc) - internship.posted_at).days
            recency_score = max(0, 100 - days_old * 2)  # Lose 2 pts per day
        else:
            recency_score = 50

        # Location preference bonus
        location_bonus = 0
        if profile:
            if profile.remote_preference == "remote" and internship.remote_status == "remote":
                location_bonus = 10
            if profile.preferred_countries:
                if internship.country and any(
                    c.lower() in (internship.country or "").lower()
                    for c in profile.preferred_countries
                ):
                    location_bonus += 5

        composite = (
            match_score * 0.6
            + overlap_score * 0.2
            + recency_score * 0.15
            + location_bonus * 0.05
        )

        # Determine recommendation reason
        reasons = []
        if match_score > 70:
            reasons.append(f"Strong match ({round(match_score)}%)")
        if overlap_count > 0:
            reasons.append(f"{overlap_count} matching skills")
        if internship.remote_status == "remote" and profile and profile.remote_preference == "remote":
            reasons.append("Remote opportunity")
        if recency_score > 80:
            reasons.append("Recently posted")

        ranked.append({
            "internship": internship,
            "composite_score": composite,
            "match_score": match_score,
            "overlap_count": overlap_count,
            "reasons": reasons or ["Based on your profile"],
        })

    # Sort by composite score
    ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    top = ranked[:limit]

    # Build response
    recommendations = []
    for item in top:
        internship = item["internship"]

        # Load company
        company_name = None
        company_logo = None
        if internship.company_id:
            comp_result = await db.execute(
                select(Company).where(Company.id == internship.company_id)
            )
            company = comp_result.scalar_one_or_none()
            if company:
                company_name = company.name
                company_logo = company.logo_url

        # Load skills
        skills_result = await db.execute(
            select(Skill.name)
            .join(InternshipSkill, InternshipSkill.skill_id == Skill.id)
            .where(InternshipSkill.internship_id == internship.id)
        )
        skill_names = [row[0] for row in skills_result.all()]

        # Check eligibility
        elig_result = await db.execute(
            select(EligibilityResult.overall_status).where(
                EligibilityResult.user_id == user_uuid,
                EligibilityResult.internship_id == internship.id,
            )
        )
        eligibility = elig_result.scalar_one_or_none()

        recommendations.append({
            "id": str(internship.id),
            "title": internship.title,
            "company_name": company_name,
            "company_logo": company_logo,
            "location": internship.location,
            "country": internship.country,
            "remote_status": internship.remote_status,
            "skills": skill_names,
            "posted_at": internship.posted_at.isoformat() if internship.posted_at else None,
            "application_deadline": str(internship.application_deadline) if internship.application_deadline else None,
            "application_url": internship.application_url,
            "match_score": round(item["match_score"], 1) if item["match_score"] else None,
            "eligibility_status": eligibility,
            "recommendation_score": round(item["composite_score"], 1),
            "reasons": item["reasons"],
        })

    return recommendations


async def _build_recommendation_list(
    db: AsyncSession,
    internships: list,
    user_uuid,
    scored_ids: dict,
    skill_overlaps: dict,
    fallback_reason: str,
) -> list[dict]:
    """Build recommendation list for fallback scenarios."""
    recommendations = []
    for internship in internships:
        company_name = None
        if internship.company_id:
            comp_result = await db.execute(
                select(Company.name).where(Company.id == internship.company_id)
            )
            company_name = comp_result.scalar_one_or_none()

        skills_result = await db.execute(
            select(Skill.name)
            .join(InternshipSkill, InternshipSkill.skill_id == Skill.id)
            .where(InternshipSkill.internship_id == internship.id)
        )
        skill_names = [row[0] for row in skills_result.all()]

        recommendations.append({
            "id": str(internship.id),
            "title": internship.title,
            "company_name": company_name,
            "company_logo": None,
            "location": internship.location,
            "country": internship.country,
            "remote_status": internship.remote_status,
            "skills": skill_names,
            "posted_at": internship.posted_at.isoformat() if internship.posted_at else None,
            "application_deadline": str(internship.application_deadline) if internship.application_deadline else None,
            "application_url": internship.application_url,
            "match_score": None,
            "eligibility_status": None,
            "recommendation_score": None,
            "reasons": [fallback_reason.replace("_", " ").title()],
        })

    return recommendations
