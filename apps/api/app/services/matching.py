"""
Match Scoring Engine.

Calculates transparent, configurable match scores between user profile and internship.
Each dimension is scored independently and combined with user-defined weights.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Default weights (user can customize)
DEFAULT_WEIGHTS = {
    "skill": 0.30,
    "education": 0.20,
    "location": 0.20,
    "experience": 0.15,
    "preference": 0.15,
}


class MatchScorer:
    """Transparent match scoring with per-dimension breakdown."""

    def __init__(self, weights: dict | None = None):
        self.weights = weights or DEFAULT_WEIGHTS.copy()

    def calculate(
        self,
        user_profile: dict,
        internship: dict,
        extracted_requirements: dict | None = None,
    ) -> dict:
        """
        Calculate overall and per-dimension match scores.
        Returns {overall_score, skill_score, education_score, location_score, experience_score, preference_score, breakdown}
        """
        reqs = extracted_requirements or {}

        skill_score = self._score_skills(user_profile, reqs)
        education_score = self._score_education(user_profile, reqs)
        location_score = self._score_location(user_profile, internship, reqs)
        experience_score = self._score_experience(user_profile, reqs)
        preference_score = self._score_preferences(user_profile, internship, reqs)

        overall = (
            skill_score * self.weights["skill"]
            + education_score * self.weights["education"]
            + location_score * self.weights["location"]
            + experience_score * self.weights["experience"]
            + preference_score * self.weights["preference"]
        )

        return {
            "overall_score": round(overall, 2),
            "skill_score": round(skill_score, 2),
            "education_score": round(education_score, 2),
            "location_score": round(location_score, 2),
            "experience_score": round(experience_score, 2),
            "preference_score": round(preference_score, 2),
            "breakdown": {
                "skill": {"score": round(skill_score, 2), "weight": self.weights["skill"]},
                "education": {"score": round(education_score, 2), "weight": self.weights["education"]},
                "location": {"score": round(location_score, 2), "weight": self.weights["location"]},
                "experience": {"score": round(experience_score, 2), "weight": self.weights["experience"]},
                "preference": {"score": round(preference_score, 2), "weight": self.weights["preference"]},
            },
        }

    def _score_skills(self, profile: dict, reqs: dict) -> float:
        """Score skill match (0-100)."""
        required = reqs.get("skills_required", [])
        preferred = reqs.get("skills_preferred", [])
        technologies = reqs.get("technologies", [])

        all_desired = set(s.lower() for s in required + preferred + technologies)
        if not all_desired:
            return 75.0  # No requirements listed = neutral score

        user_skills = set(s.lower() for s in profile.get("skills", []))

        # Required skills have higher impact
        req_lower = set(s.lower() for s in required)
        pref_lower = all_desired - req_lower

        req_matched = sum(1 for s in req_lower if any(s in us or us in s for us in user_skills))
        pref_matched = sum(1 for s in pref_lower if any(s in us or us in s for us in user_skills))

        req_count = len(req_lower) or 1
        pref_count = len(pref_lower) or 1

        req_score = (req_matched / req_count) * 70  # 70% weight for required
        pref_score = (pref_matched / pref_count) * 30  # 30% weight for preferred

        return min(100, req_score + pref_score)

    def _score_education(self, profile: dict, reqs: dict) -> float:
        """Score education match (0-100)."""
        degree_req = reqs.get("degree", {})
        if not degree_req.get("required"):
            return 80.0  # No requirement = high neutral

        score = 50.0  # Base

        # Degree level
        user_level = (profile.get("degree_level") or "").lower()
        req_level = (degree_req.get("level") or "").lower()

        if user_level and req_level:
            hierarchy = {"bachelors": 1, "masters": 2, "phd": 3}
            if hierarchy.get(user_level, 0) >= hierarchy.get(req_level, 0):
                score += 30
            else:
                score -= 20

        # Field match
        allowed_fields = [f.lower() for f in degree_req.get("fields", [])]
        user_major = (profile.get("major") or "").lower()

        if allowed_fields and user_major:
            if any(f in user_major or user_major in f for f in allowed_fields):
                score += 20
            elif "related" in allowed_fields:
                score += 10

        return max(0, min(100, score))

    def _score_location(self, profile: dict, internship: dict, reqs: dict) -> float:
        """Score location match (0-100)."""
        job_remote = reqs.get("remote_status") or internship.get("remote_status", "unknown")
        user_pref = profile.get("remote_preference", "any")

        # Remote match
        if user_pref == "any" or job_remote == "remote":
            score = 90.0
        elif user_pref == job_remote:
            score = 95.0
        elif user_pref == "remote" and job_remote != "remote":
            score = 40.0
        else:
            score = 60.0

        # Country match
        preferred_countries = profile.get("preferred_countries", [])
        job_country = reqs.get("country") or internship.get("country")

        if preferred_countries and job_country:
            if any(c.lower() in job_country.lower() for c in preferred_countries):
                score = min(100, score + 10)
            else:
                score = max(0, score - 20)

        return score

    def _score_experience(self, profile: dict, reqs: dict) -> float:
        """Score experience match (0-100)."""
        exp_req = reqs.get("experience", {})
        if not exp_req.get("required"):
            return 80.0

        min_years = exp_req.get("minimum_years", 0)
        user_years = profile.get("total_experience_years", 0)

        if min_years == 0:
            return 80.0

        if user_years >= min_years:
            return 90.0 + min(10, (user_years - min_years) * 5)
        else:
            ratio = user_years / min_years if min_years > 0 else 0
            return max(20, ratio * 70)

    def _score_preferences(self, profile: dict, internship: dict, reqs: dict) -> float:
        """Score how well the internship matches user preferences (0-100)."""
        score = 50.0  # Base

        # Preferred domains
        preferred_domains = profile.get("preferred_domains", [])
        role_category = reqs.get("role_category", "")
        if preferred_domains and role_category:
            if any(d.lower() in role_category.lower() for d in preferred_domains):
                score += 20

        # Preferred companies
        preferred_companies = profile.get("preferred_companies", [])
        company_name = internship.get("company_name", "")
        if preferred_companies and company_name:
            if any(c.lower() in company_name.lower() for c in preferred_companies):
                score += 25

        # Target roles
        target_roles = profile.get("target_roles", [])
        job_title = internship.get("title", "")
        if target_roles and job_title:
            if any(r.lower() in job_title.lower() for r in target_roles):
                score += 15

        return min(100, score)
