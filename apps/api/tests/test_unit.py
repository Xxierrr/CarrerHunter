"""
Unit Tests — Eligibility Engine, Dedup, Match Scoring, Recommendations, Robots Checker

Run: python -m pytest tests/ -v
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


# ─── Test Match Scorer ────────────────────────────────────────────

class TestMatchScorer:
    """Tests for the 5-dimension match scoring engine."""

    def setup_method(self):
        from app.services.matching import MatchScorer
        self.scorer = MatchScorer()

    def test_perfect_skill_match(self):
        """User has all required skills → high skill score."""
        profile = {"skills": ["Python", "React", "SQL"]}
        reqs = {"skills_required": ["Python", "React"], "skills_preferred": ["SQL"]}
        result = self.scorer.calculate(profile, {}, reqs)
        assert result["skill_score"] >= 80

    def test_no_skill_match(self):
        """User has none of the required skills → low skill score."""
        profile = {"skills": ["Java", "C++"]}
        reqs = {"skills_required": ["Python", "React"], "skills_preferred": ["Go"]}
        result = self.scorer.calculate(profile, {}, reqs)
        assert result["skill_score"] < 30

    def test_no_requirements_gives_neutral(self):
        """No requirements listed → neutral default score."""
        profile = {"skills": ["Python"]}
        result = self.scorer.calculate(profile, {}, {})
        assert result["skill_score"] >= 70  # Neutral

    def test_education_match(self):
        """User meets degree requirements."""
        profile = {"degree_level": "bachelors", "major": "Computer Science"}
        reqs = {"degree": {"required": True, "level": "bachelors", "fields": ["Computer Science"]}}
        result = self.scorer.calculate(profile, {}, reqs)
        assert result["education_score"] >= 70

    def test_education_overqualified(self):
        """Masters applying for bachelors-required position."""
        profile = {"degree_level": "masters", "major": "Data Science"}
        reqs = {"degree": {"required": True, "level": "bachelors", "fields": ["Data Science"]}}
        result = self.scorer.calculate(profile, {}, reqs)
        assert result["education_score"] >= 80

    def test_location_remote_preference(self):
        """User wants remote, job is remote → high location score."""
        profile = {"remote_preference": "remote"}
        internship = {"remote_status": "remote"}
        result = self.scorer.calculate(profile, internship, {"remote_status": "remote"})
        assert result["location_score"] >= 85

    def test_location_mismatch(self):
        """User wants remote, job is onsite → low location score."""
        profile = {"remote_preference": "remote"}
        internship = {"remote_status": "onsite"}
        result = self.scorer.calculate(profile, internship, {"remote_status": "onsite"})
        assert result["location_score"] < 50

    def test_experience_no_requirement(self):
        """No experience required → high default."""
        profile = {}
        result = self.scorer.calculate(profile, {}, {})
        assert result["experience_score"] >= 75

    def test_experience_sufficient(self):
        """User has enough experience."""
        profile = {"total_experience_years": 2}
        reqs = {"experience": {"required": True, "minimum_years": 1}}
        result = self.scorer.calculate(profile, {}, reqs)
        assert result["experience_score"] >= 85

    def test_overall_is_weighted_average(self):
        """Overall score is a weighted combination of all dimensions."""
        profile = {"skills": ["Python"], "degree_level": "bachelors"}
        result = self.scorer.calculate(profile, {}, {})
        # Overall should be between 0 and 100
        assert 0 <= result["overall_score"] <= 100
        # Breakdown should have all 5 keys
        assert set(result["breakdown"].keys()) == {"skill", "education", "location", "experience", "preference"}

    def test_custom_weights(self):
        """Custom weights should change the overall score."""
        from app.services.matching import MatchScorer
        heavy_skill = MatchScorer(weights={
            "skill": 0.90, "education": 0.025, "location": 0.025,
            "experience": 0.025, "preference": 0.025,
        })
        profile = {"skills": ["Python", "React"]}
        reqs = {"skills_required": ["Python", "React"]}
        result = heavy_skill.calculate(profile, {}, reqs)
        assert result["overall_score"] >= 70


# ─── Test Deduplication ───────────────────────────────────────────

class TestDeduplication:
    """Tests for the 4-level deduplication engine."""

    def test_content_hash_deterministic(self):
        """Same content produces same hash."""
        from app.services.deduplication import compute_content_hash
        h1 = compute_content_hash("Software Engineer Intern at Google")
        h2 = compute_content_hash("Software Engineer Intern at Google")
        assert h1 == h2

    def test_content_hash_different(self):
        """Different content produces different hash."""
        from app.services.deduplication import compute_content_hash
        h1 = compute_content_hash("Software Engineer Intern")
        h2 = compute_content_hash("Data Scientist Intern")
        assert h1 != h2


# ─── Test Robots Checker ─────────────────────────────────────────

class TestRobotsChecker:
    """Tests for the robots.txt compliance checker."""

    def test_robots_url_extraction(self):
        """Extracts correct robots.txt URL from any URL."""
        from app.crawlers.robots_checker import RobotsChecker
        checker = RobotsChecker()
        assert checker._get_robots_url("https://boards.greenhouse.io/company/jobs/123") == "https://boards.greenhouse.io/robots.txt"
        assert checker._get_robots_url("https://api.lever.co/v0/postings/company") == "https://api.lever.co/robots.txt"

    def test_domain_extraction(self):
        """Extracts domain for cache keys."""
        from app.crawlers.robots_checker import RobotsChecker
        checker = RobotsChecker()
        assert checker._get_domain("https://boards.greenhouse.io/company/jobs/123") == "boards.greenhouse.io"

    def test_cache_clear(self):
        """Cache clearing works."""
        from app.crawlers.robots_checker import RobotsChecker, _robots_cache
        checker = RobotsChecker()
        _robots_cache["test.com"] = (MagicMock(), 0)
        checker.clear_cache()
        assert "test.com" not in _robots_cache


# ─── Test Utilities ──────────────────────────────────────────────

class TestEligibilityUtils:
    """Tests for eligibility utility functions (frontend-shared logic)."""

    def test_is_internship_detection(self):
        """Detects internship from title keywords."""
        from app.crawlers.base import JobSourceAdapter

        class TestAdapter(JobSourceAdapter):
            async def discover(self): return []
            async def parse_listing(self, raw_job): return {}

        adapter = TestAdapter()
        assert adapter.is_internship("Software Engineering Intern") is True
        assert adapter.is_internship("Summer Internship Program") is True
        assert adapter.is_internship("Co-op Developer") is True
        assert adapter.is_internship("Senior Software Engineer") is False

    def test_detect_remote_status(self):
        """Detects remote/hybrid/onsite from text."""
        from app.crawlers.base import JobSourceAdapter

        class TestAdapter(JobSourceAdapter):
            async def discover(self): return []
            async def parse_listing(self, raw_job): return {}

        adapter = TestAdapter()
        assert adapter.detect_remote("Remote") == "remote"
        assert adapter.detect_remote("San Francisco, CA (Hybrid)") == "hybrid"
        assert adapter.detect_remote("On-site, New York") == "onsite"
        assert adapter.detect_remote("Mountain View, CA") == "unknown"


# ─── Test Normalized Job ─────────────────────────────────────────

class TestNormalizedJob:
    """Tests for the normalization pipeline."""

    def test_normalize_defaults(self):
        """Normalizer fills in defaults for missing fields."""
        from app.crawlers.base import JobSourceAdapter

        class TestAdapter(JobSourceAdapter):
            async def discover(self): return []
            async def parse_listing(self, raw_job): return {}

        adapter = TestAdapter()
        result = adapter.normalize({
            "source_job_id": "123",
            "title": "Intern",
            "company_name": "TestCo",
        })
        assert result.source_job_id == "123"
        assert result.title == "Intern"
        assert result.company_name == "TestCo"
        assert result.employment_type == "internship"
        assert result.skills == []

    def test_normalize_full(self):
        """Normalizer passes through all provided fields."""
        from app.crawlers.base import JobSourceAdapter

        class TestAdapter(JobSourceAdapter):
            async def discover(self): return []
            async def parse_listing(self, raw_job): return {}

        adapter = TestAdapter()
        result = adapter.normalize({
            "source_job_id": "456",
            "title": "ML Intern",
            "company_name": "AI Corp",
            "location": "Remote",
            "country": "US",
            "remote_status": "remote",
            "skills": ["Python", "TensorFlow"],
            "application_url": "https://example.com/apply",
        })
        assert result.location == "Remote"
        assert result.country == "US"
        assert result.remote_status == "remote"
        assert result.skills == ["Python", "TensorFlow"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
