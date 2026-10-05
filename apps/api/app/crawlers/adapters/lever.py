"""
Lever ATS Adapter.

Lever provides a public JSON API for job postings:
  https://api.lever.co/v0/postings/{company}?mode=json
  
Public API, no authentication required.
"""

import logging

from app.crawlers.base import JobSourceAdapter, RawJob, AutomationStatus
from app.crawlers.registry import register_adapter

logger = logging.getLogger(__name__)


@register_adapter("lever")
class LeverAdapter(JobSourceAdapter):
    """Adapter for Lever ATS public job postings API."""

    source_type = "ats"
    automation_status = AutomationStatus.SUPPORTED

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.company_slug = self.config.get("company_slug", "")
        self.company_name = self.config.get("company_name", "")
        self.base_url = f"https://api.lever.co/v0/postings/{self.company_slug}"

    async def discover(self) -> list[RawJob]:
        """Fetch all postings from Lever API."""
        if not self.company_slug:
            logger.error("Lever adapter: no company_slug configured")
            return []

        client = await self.get_http_client()
        try:
            response = await client.get(f"{self.base_url}?mode=json")
            response.raise_for_status()
            postings = response.json()
        except Exception as e:
            logger.error(f"Lever API error for {self.company_name}: {e}")
            return []

        if not isinstance(postings, list):
            logger.error(f"Lever returned non-list for {self.company_name}")
            return []

        jobs = []
        for posting in postings:
            title = posting.get("text", "")
            description = posting.get("descriptionPlain", "") or posting.get("description", "")

            if not self.is_internship(title, description):
                continue

            location = ""
            if posting.get("categories", {}).get("location"):
                location = posting["categories"]["location"]

            jobs.append(RawJob(
                source_job_id=posting.get("id", ""),
                title=title,
                company=self.company_name,
                description=description,
                location=location,
                url=posting.get("hostedUrl", ""),
                application_url=posting.get("applyUrl", posting.get("hostedUrl", "")),
                raw_data=posting,
                metadata={
                    "team": posting.get("categories", {}).get("team"),
                    "department": posting.get("categories", {}).get("department"),
                    "commitment": posting.get("categories", {}).get("commitment"),
                },
            ))

        logger.info(f"Lever/{self.company_name}: found {len(jobs)} internships")
        return jobs

    async def parse_listing(self, raw_job: RawJob) -> dict:
        """Parse Lever posting data."""
        data = raw_job.raw_data
        location = raw_job.location or ""

        # Extract country from location
        country = None
        if location:
            parts = [p.strip() for p in location.split(",")]
            if len(parts) >= 2:
                country = parts[-1]

        return {
            "source_job_id": raw_job.source_job_id,
            "title": raw_job.title,
            "company_name": self.company_name,
            "description": raw_job.description,
            "location": location,
            "country": country,
            "remote_status": self.detect_remote(location, raw_job.description),
            "employment_type": "internship",
            "application_url": raw_job.application_url,
            "source_url": raw_job.url,
            "posted_at": str(data.get("createdAt", "")),
            "raw_content": raw_job.description,
            "skills": [],
        }
