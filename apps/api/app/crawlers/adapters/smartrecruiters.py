"""
SmartRecruiters ATS Adapter.

SmartRecruiters provides a public API:
  https://api.smartrecruiters.com/v1/companies/{company_id}/postings
  
Public API, no authentication required for job postings.
"""

import logging

from app.crawlers.base import JobSourceAdapter, RawJob, AutomationStatus
from app.crawlers.registry import register_adapter

logger = logging.getLogger(__name__)


@register_adapter("smartrecruiters")
class SmartRecruitersAdapter(JobSourceAdapter):
    """Adapter for SmartRecruiters public postings API."""

    source_type = "ats"
    automation_status = AutomationStatus.SUPPORTED

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.company_id = self.config.get("company_id", "")
        self.company_name = self.config.get("company_name", "")
        self.base_url = f"https://api.smartrecruiters.com/v1/companies/{self.company_id}/postings"

    async def discover(self) -> list[RawJob]:
        """Fetch all postings from SmartRecruiters API."""
        if not self.company_id:
            logger.error("SmartRecruiters adapter: no company_id configured")
            return []

        client = await self.get_http_client()
        all_jobs = []
        offset = 0
        limit = 100

        while True:
            try:
                response = await client.get(
                    self.base_url,
                    params={"offset": offset, "limit": limit},
                )
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"SmartRecruiters API error for {self.company_name}: {e}")
                break

            postings = data.get("content", [])
            if not postings:
                break

            for posting in postings:
                title = posting.get("name", "")
                description = posting.get("jobDescription", {}).get("text", "") if isinstance(posting.get("jobDescription"), dict) else ""

                if not self.is_internship(title, description):
                    continue

                location_data = posting.get("location", {})
                location = ""
                country = None
                if location_data:
                    city = location_data.get("city", "")
                    region = location_data.get("region", "")
                    country = location_data.get("country", "")
                    parts = [p for p in [city, region, country] if p]
                    location = ", ".join(parts)

                all_jobs.append(RawJob(
                    source_job_id=str(posting.get("id", "")),
                    title=title,
                    company=self.company_name,
                    description=description,
                    location=location,
                    url=posting.get("ref", ""),
                    application_url=posting.get("applyUrl", posting.get("ref", "")),
                    raw_data=posting,
                    metadata={
                        "department": posting.get("department", {}).get("label", ""),
                        "country": country,
                    },
                ))

            if len(postings) < limit:
                break
            offset += limit

        logger.info(f"SmartRecruiters/{self.company_name}: found {len(all_jobs)} internships")
        return all_jobs

    async def parse_listing(self, raw_job: RawJob) -> dict:
        """Parse SmartRecruiters posting data."""
        return {
            "source_job_id": raw_job.source_job_id,
            "title": raw_job.title,
            "company_name": self.company_name,
            "description": raw_job.description,
            "location": raw_job.location,
            "country": raw_job.metadata.get("country"),
            "remote_status": self.detect_remote(raw_job.location, raw_job.description),
            "employment_type": "internship",
            "application_url": raw_job.application_url,
            "source_url": raw_job.url,
            "raw_content": raw_job.description,
            "skills": [],
        }
