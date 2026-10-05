"""
Integration Tests — API endpoints, adapter framework, crawl pipeline.

These tests verify the full request-response cycle for API routes
and the adapter registration/discovery framework.

Run: python -m pytest tests/test_integration.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


# ─── Test Adapter Registry ───────────────────────────────────────

class TestAdapterRegistry:
    """Tests for the source adapter registry."""

    def test_load_all_adapters(self):
        """All adapters load without errors."""
        from app.crawlers.registry import load_all_adapters, list_adapters
        load_all_adapters()
        adapters = list_adapters()
        assert len(adapters) >= 4  # greenhouse, lever, ashby, smartrecruiters

    def test_get_adapter_by_name(self):
        """Can retrieve registered adapters by name."""
        from app.crawlers.registry import load_all_adapters, get_adapter
        load_all_adapters()
        adapter = get_adapter("greenhouse", config={"company_slug": "test"})
        assert adapter is not None
        assert adapter.name == "greenhouse"

    def test_get_adapter_unknown_raises(self):
        """Unknown adapter name raises ValueError."""
        from app.crawlers.registry import get_adapter
        with pytest.raises(ValueError, match="Unknown adapter"):
            get_adapter("nonexistent_adapter_xyz")

    def test_all_adapters_have_required_methods(self):
        """Every registered adapter implements discover() and parse_listing()."""
        from app.crawlers.registry import load_all_adapters, list_adapters
        load_all_adapters()
        for name, adapter_cls in list_adapters().items():
            assert hasattr(adapter_cls, "discover"), f"{name} missing discover()"
            assert hasattr(adapter_cls, "parse_listing"), f"{name} missing parse_listing()"
            assert hasattr(adapter_cls, "normalize"), f"{name} missing normalize()"


# ─── Test Adapter Implementations ────────────────────────────────

class TestGreenhouseAdapter:
    """Tests for the Greenhouse adapter."""

    def test_adapter_initialization(self):
        """Greenhouse adapter initializes with config."""
        from app.crawlers.registry import load_all_adapters, get_adapter
        load_all_adapters()
        adapter = get_adapter("greenhouse", config={
            "company_slug": "testcompany",
            "company_name": "Test Company",
        })
        assert adapter.config["company_slug"] == "testcompany"

    def test_normalize_output(self):
        """Adapter normalize produces NormalizedJob."""
        from app.crawlers.registry import load_all_adapters, get_adapter
        from app.crawlers.base import NormalizedJob
        load_all_adapters()
        adapter = get_adapter("greenhouse", config={
            "company_slug": "test",
            "company_name": "Test Co",
        })
        result = adapter.normalize({
            "source_job_id": "gh_123",
            "title": "Software Intern",
            "company_name": "Test Co",
            "location": "San Francisco",
        })
        assert isinstance(result, NormalizedJob)
        assert result.title == "Software Intern"


class TestLeverAdapter:
    """Tests for the Lever adapter."""

    def test_adapter_initialization(self):
        from app.crawlers.registry import load_all_adapters, get_adapter
        load_all_adapters()
        adapter = get_adapter("lever", config={
            "company_slug": "testlever",
            "company_name": "Lever Test",
        })
        assert adapter.config["company_slug"] == "testlever"


# ─── Test Crawl Pipeline Components ─────────────────────────────

class TestCrawlPipeline:
    """Tests for individual crawl pipeline components."""

    def test_content_hash_consistency(self):
        """Same input always produces same hash for dedup."""
        from app.services.deduplication import compute_content_hash
        content = "Software Engineering Intern\nBuild cool things"
        h1 = compute_content_hash(content)
        h2 = compute_content_hash(content)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex digest

    def test_content_hash_sensitivity(self):
        """Slightly different content produces different hashes."""
        from app.services.deduplication import compute_content_hash
        h1 = compute_content_hash("Software Engineer Intern")
        h2 = compute_content_hash("Software Engineer Intern 2024")
        assert h1 != h2


# ─── Test Seed Sources ───────────────────────────────────────────

class TestSeedSources:
    """Tests for the source configuration seeding."""

    def test_seed_sources_data(self):
        """Seed sources data is well-structured."""
        from app.crawlers.seed_sources import INITIAL_SOURCES
        assert len(INITIAL_SOURCES) >= 10
        for source in INITIAL_SOURCES:
            assert "name" in source
            assert "adapter_name" in source
            assert "base_url" in source


# ─── Test Email Templates ────────────────────────────────────────

class TestEmailTemplates:
    """Tests for email template generation."""

    def test_new_match_email(self):
        """New match email generates valid HTML."""
        from app.email.templates import new_match_email
        result = new_match_email(
            internship={
                "company_name": "Google",
                "title": "SWE Intern",
                "location": "Mountain View",
                "remote_status": "onsite",
                "skills": ["Python", "C++"],
                "application_url": "https://google.com/apply",
            },
            match_info={
                "match_score": 87,
                "eligibility_status": "Eligible",
            },
        )
        assert "subject" in result
        assert "html" in result
        assert "Google" in result["html"]
        assert "SWE Intern" in result["subject"]

    def test_deadline_reminder_email(self):
        """Deadline reminder generates valid HTML."""
        from app.email.templates import deadline_reminder_email
        result = deadline_reminder_email(
            internship={
                "company_name": "Meta",
                "title": "ML Intern",
                "application_url": "https://meta.com/apply",
            },
            days_remaining=3,
        )
        assert "3 day" in result["subject"]
        assert "Meta" in result["html"]

    def test_daily_digest_email(self):
        """Daily digest generates valid HTML."""
        from app.email.templates import daily_digest_email
        result = daily_digest_email(
            matches=[
                {"company_name": "Google", "title": "SWE Intern", "match_score": 85},
                {"company_name": "Meta", "title": "ML Intern", "match_score": 72},
            ],
            stats={"new_matches": 5, "closing_soon": 2},
        )
        assert "5" in result["subject"]
        assert "Google" in result["html"]


# ─── Test Pydantic Schemas ───────────────────────────────────────

class TestSchemas:
    """Tests for Pydantic schema validation."""

    def test_internship_response_schema(self):
        """InternshipResponse accepts valid data."""
        from app.schemas.internship import InternshipResponse
        import uuid

        response = InternshipResponse(
            id=uuid.uuid4(),
            title="SWE Intern",
            company_name="Google",
            status="active",
        )
        assert response.title == "SWE Intern"
        assert response.is_saved is False
        assert response.skills == []

    def test_internship_search_params(self):
        """Search params have correct defaults."""
        from app.schemas.internship import InternshipSearchParams

        params = InternshipSearchParams()
        assert params.page == 1
        assert params.limit == 20
        assert params.sort == "posted_at"
        assert params.order == "desc"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
