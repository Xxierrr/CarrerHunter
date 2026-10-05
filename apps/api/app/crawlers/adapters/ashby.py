"""
Ashby ATS Adapter.

Ashby provides a public posting API:
  https://api.ashbyhq.com/posting-api/job-board/{board_slug}
  
Public API, no authentication required.
"""

import logging

from app.crawlers.base import JobSourceAdapter, RawJob, AutomationStatus
from app.crawlers.registry import register_adapter

logger = logging.getLogger(__name__)


@register_adapter("ashby")
class AshbyAdapter(JobSourceAdapter):
    """Adapter for Ashby ATS public job board API."""

    source_type = "ats"
    automation_status = AutomationStatus.SUPPORTED

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.board_slug = self.config.get("board_slug", "")
        self.company_name = self.config.get("company_name", "")
        self.base_url = f"https://api.ashbyhq.com/posting-api/job-board/{self.board_slug}"

    async def discover(self) -> list[RawJob]:
        """Fetch all jobs from Ashby board API."""
        if not self.board_slug:
            logger.error("Ashby adapter: no board_slug configured")
            return []

        client = await self.get_http_client()
        try:
            response = await client.get(self.base_url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Ashby API error for {self.company_name}: {e}")
            return []

        jobs = []
        for job_data in data.get("jobs", []):
            title = job_data.get("title", "")
            description = job_data.get("descriptionPlain", "") or job_data.get("description", "")

            if not self.is_internship(title, description):
                continue

            location = job_data.get("location", "")
            if isinstance(location, dict):
                location = location.get("name", "")

            jobs.append(RawJob(
                source_job_id=str(job_data.get("id", "")),
                title=title,
                company=self.company_name,
                description=description,
                location=location if isinstance(location, str) else "",
                url=job_data.get("jobUrl", ""),
                application_url=job_data.get("applyUrl", job_data.get("jobUrl", "")),
                raw_data=job_data,
                metadata={
                    "department": job_data.get("department", ""),
                    "team": job_data.get("team", ""),
                    "employment_type": job_data.get("employmentType", ""),
                },
            ))

        logger.info(f"Ashby/{self.company_name}: found {len(jobs)} internships")
        return jobs

    async def parse_listing(self, raw_job: RawJob) -> dict:
        """Parse Ashby posting data."""
        location = raw_job.location or ""
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
            "raw_content": raw_job.description,
            "skills": [],
        }
