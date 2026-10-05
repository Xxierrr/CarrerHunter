"""
Two-Stage Eligibility Engine.

Stage 1: Deterministic — checks hard criteria with code (no AI needed)
Stage 2: AI Interpretation — uses Gemini only for ambiguous NLP requirements

The engine NEVER fabricates requirements or claims certainty when ambiguous.
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)


# Eligibility statuses ordered from most to least favorable
ELIGIBILITY_STATUSES = [
    "eligible",
    "likely_eligible",
    "possibly_eligible",
    "uncertain",
    "likely_ineligible",
    "ineligible",
]

# Criterion results
PASS = "pass"
FAIL = "fail"
UNKNOWN = "unknown"


def _criterion(
    requirement: str,
    candidate_value: Any,
    job_requirement: Any,
    result: str,
    source_text: str = "",
    confidence: float = 1.0,
    method: str = "deterministic",
) -> dict:
    """Build a standardized eligibility criterion result."""
    return {
        "requirement": requirement,
        "candidate_value": str(candidate_value) if candidate_value is not None else "Not provided",
        "job_requirement": str(job_requirement) if job_requirement is not None else "Not specified",
        "result": result,
        "source_text": source_text,
        "confidence": confidence,
        "method": method,
    }


class EligibilityEngine:
    """
    Two-stage eligibility engine.
    
    Stage 1 runs deterministic checks for clear-cut requirements.
    Stage 2 uses AI to interpret ambiguous NLP requirements.
    """

    def calculate_deterministic(
        self,
        user_profile: dict,
        internship: dict,
        extracted_requirements: dict | None = None,
    ) -> list[dict]:
        """
        Stage 1: Deterministic eligibility checks.
        Returns list of criterion results: {requirement, candidate_value, job_requirement, result, ...}
        """
        criteria = []
        reqs = extracted_requirements or {}

        # --- Degree Level ---
        degree_req = reqs.get("degree", {})
        if degree_req.get("required"):
            user_degree = user_profile.get("degree_level", "").lower()
            req_level = (degree_req.get("level") or "").lower()

            if req_level and user_degree:
                degree_hierarchy = {"bachelors": 1, "masters": 2, "phd": 3}
                user_rank = degree_hierarchy.get(user_degree, 0)
                req_rank = degree_hierarchy.get(req_level, 0)

                if user_rank >= req_rank:
                    result = PASS
                elif req_level in ["any", ""]:
                    result = PASS
                else:
                    result = FAIL

                criteria.append(_criterion(
                    requirement=f"Degree: {req_level}",
                    candidate_value=user_profile.get("degree", user_degree),
                    job_requirement=req_level,
                    result=result,
                    source_text=degree_req.get("source_text", ""),
                ))
            else:
                criteria.append(_criterion(
                    requirement="Degree requirement",
                    candidate_value=user_profile.get("degree", "Not provided"),
                    job_requirement=req_level or "Required (level unknown)",
                    result=UNKNOWN,
                    source_text=degree_req.get("source_text", ""),
                ))

        # --- Field of Study ---
        if degree_req.get("fields"):
            user_major = (user_profile.get("major") or "").lower()
            allowed_fields = [f.lower() for f in degree_req["fields"]]

            if user_major:
                # Check if user's major matches any allowed field
                match = any(
                    field in user_major or user_major in field
                    for field in allowed_fields
                ) or "related" in allowed_fields

                criteria.append(_criterion(
                    requirement="Field of study",
                    candidate_value=user_profile.get("major"),
                    job_requirement=", ".join(degree_req["fields"]),
                    result=PASS if match else FAIL,
                    source_text=degree_req.get("source_text", ""),
                    confidence=0.8 if "related" in allowed_fields else 0.95,
                ))
            else:
                criteria.append(_criterion(
                    requirement="Field of study",
                    candidate_value="Not provided",
                    job_requirement=", ".join(degree_req["fields"]),
                    result=UNKNOWN,
                ))

        # --- GPA ---
        gpa_req = reqs.get("gpa_minimum")
        if gpa_req is not None:
            user_gpa = user_profile.get("gpa")
            user_scale = user_profile.get("gpa_scale", 10.0)

            if user_gpa is not None:
                # Normalize to 4.0 scale for comparison if needed
                try:
                    user_gpa_f = float(user_gpa)
                    req_gpa_f = float(gpa_req)

                    if float(user_scale) == 10.0 and req_gpa_f <= 4.0:
                        # Convert user's 10-point GPA to 4.0 scale
                        user_gpa_normalized = user_gpa_f * 0.4
                    elif float(user_scale) == 4.0:
                        user_gpa_normalized = user_gpa_f
                    else:
                        user_gpa_normalized = user_gpa_f

                    criteria.append(_criterion(
                        requirement=f"Minimum GPA: {gpa_req}",
                        candidate_value=f"{user_gpa} / {user_scale}",
                        job_requirement=str(gpa_req),
                        result=PASS if user_gpa_normalized >= req_gpa_f else FAIL,
                        confidence=0.85,
                    ))
                except (ValueError, TypeError):
                    criteria.append(_criterion(
                        requirement=f"Minimum GPA: {gpa_req}",
                        candidate_value=str(user_gpa),
                        job_requirement=str(gpa_req),
                        result=UNKNOWN,
                    ))

        # --- Graduation Year ---
        grad_req = reqs.get("graduation", {})
        user_grad = user_profile.get("graduation_date")
        if grad_req and user_grad:
            try:
                if isinstance(user_grad, str):
                    user_grad_date = date.fromisoformat(user_grad)
                else:
                    user_grad_date = user_grad
                user_grad_year = user_grad_date.year

                min_year = grad_req.get("minimum_year")
                max_year = grad_req.get("maximum_year")

                if min_year and max_year:
                    result = PASS if min_year <= user_grad_year <= max_year else FAIL
                elif min_year:
                    result = PASS if user_grad_year >= min_year else FAIL
                elif max_year:
                    result = PASS if user_grad_year <= max_year else FAIL
                else:
                    result = UNKNOWN

                criteria.append(_criterion(
                    requirement="Graduation year",
                    candidate_value=str(user_grad_year),
                    job_requirement=f"{min_year or '?'} - {max_year or '?'}",
                    result=result,
                    source_text=grad_req.get("source_text", ""),
                ))
            except (ValueError, AttributeError):
                pass

        # --- Experience ---
        exp_req = reqs.get("experience", {})
        if exp_req.get("required") and exp_req.get("minimum_years") is not None:
            user_exp_years = user_profile.get("total_experience_years", 0)
            min_years = exp_req["minimum_years"]

            criteria.append(_criterion(
                requirement=f"Experience: {min_years}+ years",
                candidate_value=f"{user_exp_years} years",
                job_requirement=f"{min_years} years",
                result=PASS if user_exp_years >= min_years else FAIL,
                source_text=exp_req.get("source_text", ""),
            ))

        # --- Skills Match ---
        required_skills = reqs.get("skills_required", [])
        user_skills = [s.lower() for s in user_profile.get("skills", [])]

        if required_skills:
            matched = []
            unmatched = []
            for skill in required_skills:
                skill_lower = skill.lower()
                if any(skill_lower in us or us in skill_lower for us in user_skills):
                    matched.append(skill)
                else:
                    unmatched.append(skill)

            for skill in matched:
                criteria.append(_criterion(
                    requirement=f"Required skill: {skill}",
                    candidate_value="Has skill",
                    job_requirement=skill,
                    result=PASS,
                ))

            for skill in unmatched:
                criteria.append(_criterion(
                    requirement=f"Required skill: {skill}",
                    candidate_value="Missing",
                    job_requirement=skill,
                    result=FAIL,
                    confidence=0.8,
                ))

        # --- Remote Status ---
        remote_pref = user_profile.get("remote_preference")
        job_remote = reqs.get("remote_status") or internship.get("remote_status")

        if remote_pref and job_remote and job_remote != "unknown":
            if remote_pref == "any":
                result = PASS
            elif remote_pref == job_remote:
                result = PASS
            elif remote_pref == "remote" and job_remote == "hybrid":
                result = PASS  # Remote-preferred user can do hybrid
            else:
                result = FAIL

            criteria.append(_criterion(
                requirement="Work mode",
                candidate_value=remote_pref,
                job_requirement=job_remote,
                result=result,
            ))

        # --- Location / Country ---
        preferred_countries = user_profile.get("preferred_countries", [])
        job_country = reqs.get("country") or internship.get("country")

        if preferred_countries and job_country:
            country_match = any(
                c.lower() in job_country.lower() or job_country.lower() in c.lower()
                for c in preferred_countries
            )
            criteria.append(_criterion(
                requirement="Country preference",
                candidate_value=", ".join(preferred_countries),
                job_requirement=job_country,
                result=PASS if country_match else FAIL,
                confidence=0.9,
            ))

        # --- Work Authorization ---
        work_auth_req = reqs.get("work_authorization", {})
        if work_auth_req.get("required"):
            user_auth = user_profile.get("work_authorization", {})
            if user_auth:
                criteria.append(_criterion(
                    requirement="Work authorization",
                    candidate_value=str(user_auth),
                    job_requirement=work_auth_req.get("details", "Required"),
                    result=UNKNOWN,  # Usually requires human review
                    source_text=work_auth_req.get("source_text", ""),
                    confidence=0.5,
                    method="requires_review",
                ))

        return criteria

    def aggregate_status(self, criteria: list[dict]) -> str:
        """
        Determine overall eligibility status from individual criteria.
        Conservative: uncertain when evidence is mixed.
        """
        if not criteria:
            return "uncertain"

        passes = sum(1 for c in criteria if c["result"] == PASS)
        fails = sum(1 for c in criteria if c["result"] == FAIL)
        unknowns = sum(1 for c in criteria if c["result"] == UNKNOWN)
        total = len(criteria)

        if fails == 0 and unknowns == 0:
            return "eligible"
        elif fails == 0 and unknowns > 0:
            return "likely_eligible"
        elif fails <= 1 and passes > fails:
            if unknowns > 0:
                return "possibly_eligible"
            return "likely_eligible"
        elif fails > 0 and passes >= fails:
            return "uncertain"
        elif fails > passes:
            return "likely_ineligible"
        else:
            return "uncertain"

    def calculate_deterministic_score(self, criteria: list[dict]) -> float:
        """Calculate a numerical score from criteria (0-100)."""
        if not criteria:
            return 50.0

        weights = {PASS: 1.0, UNKNOWN: 0.5, FAIL: 0.0}
        total_weight = 0
        weighted_sum = 0

        for c in criteria:
            confidence = c.get("confidence", 1.0)
            score = weights.get(c["result"], 0.5)
            weighted_sum += score * confidence
            total_weight += confidence

        if total_weight == 0:
            return 50.0

        return round((weighted_sum / total_weight) * 100, 2)
