"""
Greenhouse ATS Adapter.

Greenhouse provides a public JSON API for job boards:
  https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
  
This is a public, documented API designed for consumption.
No authentication required. Rate limits should be respected.
"""

import logging
from datetime import datetime

from app.crawlers.base import JobSourceAdapter, RawJob, AutomationStatus
from app.crawlers.registry import register_adapter

logger = logging.getLogger(__name__)


@register_adapter("greenhouse")
class GreenhouseAdapter(JobSourceAdapter):
    """Adapter for Greenhouse ATS public job board API."""

    source_type = "ats"
    automation_status = AutomationStatus.SUPPORTED

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.board_token = self.config.get("board_token", "")
        self.company_name = self.config.get("company_name", "")
        self.base_url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}"

    async def discover(self) -> list[RawJob]:
        """Fetch all jobs from the Greenhouse board API."""
        if not self.board_token:
            logger.error("Greenhouse adapter: no board_token configured")
            return []

        client = await self.get_http_client()
        try:
            response = await client.get(f"{self.base_url}/jobs?content=true")
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Greenhouse API error for {self.company_name}: {e}")
            return []

        jobs = []
        for job_data in data.get("jobs", []):
            title = job_data.get("title", "")
            # Filter for internships only
            if not self.is_internship(title, job_data.get("content", "")):
                continue

            location_name = ""
            if job_data.get("location"):
                location_name = job_data["location"].get("name", "")

            jobs.append(RawJob(
                source_job_id=str(job_data.get("id", "")),
                title=title,
                company=self.company_name,
                description=job_data.get("content", ""),
                location=location_name,
                url=job_data.get("absolute_url", ""),
                application_url=job_data.get("absolute_url", ""),
                raw_data=job_data,
                metadata={
                    "departments": [d.get("name") for d in job_data.get("departments", [])],
                    "updated_at": job_data.get("updated_at"),
                },
            ))

        logger.info(f"Greenhouse/{self.company_name}: found {len(jobs)} internships")
        return jobs

    async def parse_listing(self, raw_job: RawJob) -> dict:
        """Parse Greenhouse job data into structured fields."""
        data = raw_job.raw_data

        # Extract location details
        location = raw_job.location or ""
        country = None
        if location:
            # Simple country extraction from location string
            parts = [p.strip() for p in location.split(",")]
            if len(parts) >= 2:
                country = parts[-1]

        # Parse dates
        posted_at = data.get("updated_at") or data.get("first_published_at")

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
            "posted_at": posted_at,
            "raw_content": raw_job.description,
            "skills": [],  # Will be extracted by AI service
            "departments": raw_job.metadata.get("departments", []),
        }
