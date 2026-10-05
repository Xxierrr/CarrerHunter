"""
Generic Career Page Adapter — fallback for sources that don't have a public API.

Marks sources as UNSUPPORTED_AUTOMATION when direct scraping isn't permitted.
Provides the official application URL instead.
"""

import logging

from app.crawlers.base import JobSourceAdapter, RawJob, AutomationStatus
from app.crawlers.registry import register_adapter

logger = logging.getLogger(__name__)


@register_adapter("generic_career_page")
class GenericCareerPageAdapter(JobSourceAdapter):
    """
    Adapter for company career pages without public APIs.
    
    For most company career pages (Google, Microsoft, Amazon, Meta, etc.),
    direct scraping is either:
    - Prohibited by robots.txt
    - Prohibited by Terms of Service
    - Protected by anti-bot mechanisms
    
    This adapter stores the career page URL and marks the source as
    UNSUPPORTED_AUTOMATION, providing the official link for manual browsing.
    
    When a company does provide a public API or structured data feed,
    a dedicated adapter should be created instead.
    """

    source_type = "career_page"
    automation_status = AutomationStatus.UNSUPPORTED_AUTOMATION

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.company_name = self.config.get("company_name", "")
        self.career_url = self.config.get("career_url", "")
        self.base_url = self.career_url

    async def discover(self) -> list[RawJob]:
        """
        Cannot discover jobs automatically from this source.
        Returns empty list — users should visit the career page directly.
        """
        logger.info(
            f"GenericCareerPage/{self.company_name}: "
            f"UNSUPPORTED_AUTOMATION. Visit: {self.career_url}"
        )
        return []

    async def parse_listing(self, raw_job: RawJob) -> dict:
        """Not used for unsupported automation sources."""
        return {
            "source_job_id": raw_job.source_job_id,
            "title": raw_job.title,
            "company_name": self.company_name,
            "application_url": self.career_url,
            "source_url": self.career_url,
        }
