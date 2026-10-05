"""
Job Source Adapter — Abstract base class for all source adapters.
Each source (Greenhouse, Lever, career pages, etc.) implements this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import logging

logger = logging.getLogger(__name__)


class AutomationStatus(Enum):
    SUPPORTED = "supported"
    UNSUPPORTED_AUTOMATION = "unsupported_automation"


@dataclass
class RawJob:
    """Raw job data as fetched from a source, before normalization."""
    source_job_id: str
    title: str
    company: str
    description: str | None = None
    location: str | None = None
    url: str | None = None
    application_url: str | None = None
    raw_data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class NormalizedJob:
    """Job data normalized into the standard internship schema."""
    source_job_id: str
    title: str
    company_name: str
    description: str | None = None
    location: str | None = None
    country: str | None = None
    remote_status: str | None = None
    employment_type: str = "internship"
    duration_weeks: int | None = None
    start_date: str | None = None
    end_date: str | None = None
    application_deadline: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    skills: list[str] = field(default_factory=list)
    application_url: str | None = None
    source_url: str | None = None
    posted_at: str | None = None
    raw_content: str | None = None
    content_hash: str | None = None


class JobSourceAdapter(ABC):
    """
    Abstract base class for all job source adapters.
    
    Each adapter:
    1. Discovers job listings from its source
    2. Fetches individual listing details
    3. Parses raw data into structured fields
    4. Normalizes into the standard schema
    5. Detects changes via content hashing
    """

    name: str = "unknown"
    source_type: str = "unknown"  # career_page, ats, api, rss
    base_url: str = ""
    automation_status: AutomationStatus = AutomationStatus.SUPPORTED

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self._http_client = None

    async def get_http_client(self):
        """Lazy-initialize HTTP client."""
        if self._http_client is None:
            import httpx
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "InternshipIntel/1.0 (internship-search-bot; +https://github.com/internship-intel)",
                    "Accept": "application/json, text/html",
                },
            )
        return self._http_client

    async def close(self):
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    @abstractmethod
    async def discover(self) -> list[RawJob]:
        """
        Discover job listings from this source.
        Returns a list of RawJob objects with at minimum: source_job_id, title, company.
        """
        ...

    async def fetch_listing(self, raw_job: RawJob) -> RawJob:
        """
        Fetch full details for a single listing.
        Default implementation returns the raw job as-is (useful when discover() already fetches full data).
        """
        return raw_job

    @abstractmethod
    async def parse_listing(self, raw_job: RawJob) -> dict:
        """Parse raw job data into structured fields."""
        ...

    def normalize(self, parsed: dict) -> NormalizedJob:
        """Normalize parsed data into the standard schema."""
        return NormalizedJob(
            source_job_id=parsed.get("source_job_id", ""),
            title=parsed.get("title", "Unknown"),
            company_name=parsed.get("company_name", "Unknown"),
            description=parsed.get("description"),
            location=parsed.get("location"),
            country=parsed.get("country"),
            remote_status=parsed.get("remote_status"),
            employment_type=parsed.get("employment_type", "internship"),
            duration_weeks=parsed.get("duration_weeks"),
            application_deadline=parsed.get("application_deadline"),
            salary_min=parsed.get("salary_min"),
            salary_max=parsed.get("salary_max"),
            salary_currency=parsed.get("salary_currency"),
            skills=parsed.get("skills", []),
            application_url=parsed.get("application_url"),
            source_url=parsed.get("source_url"),
            posted_at=parsed.get("posted_at"),
            raw_content=parsed.get("raw_content"),
        )

    def is_internship(self, title: str, description: str | None = None) -> bool:
        """Heuristic check if a job posting is likely an internship."""
        text = f"{title} {description or ''}".lower()
        internship_keywords = [
            "intern", "internship", "co-op", "coop", "trainee",
            "fellowship", "apprentice", "working student", "werkstudent",
            "practicum", "placement",
        ]
        return any(keyword in text for keyword in internship_keywords)

    def detect_remote(self, location: str | None, description: str | None = None) -> str:
        """Detect remote/hybrid/onsite status from location or description."""
        text = f"{location or ''} {description or ''}".lower()
        if any(word in text for word in ["hybrid", "partial remote"]):
            return "hybrid"
        if any(word in text for word in ["remote", "work from home", "wfh", "anywhere"]):
            return "remote"
        if any(word in text for word in ["onsite", "on-site", "in-office", "in office"]):
            return "onsite"
        return "unknown"

