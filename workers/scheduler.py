"""
Background Worker Scheduler.

Runs periodic tasks:
- Source crawling (with robots.txt compliance)
- Job processing (normalize, deduplicate, extract requirements)
- Eligibility calculation
- Digest email sending
- Notification sending
- Maintenance (expire jobs, clean cache)

Uses APScheduler with asyncio for simplicity (no Celery/Redis broker needed for MVP).
"""

import asyncio
import logging
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import async_session_factory
from app.models.internship import Source, Internship, Company
from app.models.system import CrawlRun
from app.crawlers.registry import get_adapter, load_all_adapters
from app.crawlers.robots_checker import get_robots_checker
from app.services.deduplication import find_duplicate, compute_content_hash

logger = logging.getLogger(__name__)
settings = get_settings()


async def crawl_source(source_id: str):
    """Crawl a single source: discover, fetch, parse, normalize, deduplicate, store."""
    async with async_session_factory() as db:
        try:
            # Load source config
            result = await db.execute(
                select(Source).where(Source.id == source_id)
            )
            source = result.scalar_one_or_none()
            if not source or not source.enabled:
                return

            if source.automation_status == "unsupported_automation":
                logger.info(f"Skipping {source.name}: UNSUPPORTED_AUTOMATION")
                return

            # Create crawl run record
            crawl_run = CrawlRun(
                source_id=source.id,
                status="running",
            )
            db.add(crawl_run)
            await db.flush()

            start_time = time.monotonic()

            # robots.txt check
            if source.base_url:
                robots = get_robots_checker()
                if not await robots.can_fetch(source.base_url):
                    logger.info(f"Skipping {source.name}: blocked by robots.txt")
                    crawl_run.status = "skipped"
                    crawl_run.error = "Blocked by robots.txt"
                    crawl_run.completed_at = datetime.now(timezone.utc)
                    await db.commit()
                    return

                # Respect crawl-delay if specified
                crawl_delay = await robots.get_crawl_delay(source.base_url)
                if crawl_delay and crawl_delay > 0:
                    logger.info(f"Respecting crawl-delay of {crawl_delay}s for {source.name}")
                    await asyncio.sleep(min(crawl_delay, 30))  # Cap at 30s

            # Get adapter
            adapter = get_adapter(source.adapter_name, config=source.config)

            try:
                # Discover jobs
                raw_jobs = await adapter.discover()
                crawl_run.jobs_found = len(raw_jobs)

                jobs_new = 0
                jobs_updated = 0
                jobs_unchanged = 0

                for raw_job in raw_jobs:
                    try:
                        # Parse
                        parsed = await adapter.parse_listing(raw_job)
                        normalized = adapter.normalize(parsed)

                        # Content hash for change detection
                        content_hash = compute_content_hash(
                            f"{normalized.title}{normalized.description or ''}"
                        )

                        # Find or create company
                        company_name = normalized.company_name
                        comp_result = await db.execute(
                            select(Company).where(
                                Company.normalized_name == company_name.lower().strip()
                            )
                        )
                        company = comp_result.scalar_one_or_none()
                        if not company:
                            company = Company(
                                name=company_name,
                                normalized_name=company_name.lower().strip(),
                            )
                            db.add(company)
                            await db.flush()

                        # Deduplicate
                        existing = await find_duplicate(
                            db=db,
                            source_id=str(source.id),
                            source_job_id=normalized.source_job_id,
                            company_name=company_name,
                            title=normalized.title,
                            location=normalized.location,
                            application_url=normalized.application_url,
                            content_hash=content_hash,
                        )

                        if existing:
                            if existing.content_hash != content_hash:
                                # Update existing
                                existing.description = normalized.description
                                existing.location = normalized.location
                                existing.remote_status = normalized.remote_status
                                existing.application_url = normalized.application_url
                                existing.content_hash = content_hash
                                existing.last_seen_at = datetime.now(timezone.utc)
                                existing.raw_content = normalized.raw_content
                                jobs_updated += 1
                            else:
                                existing.last_seen_at = datetime.now(timezone.utc)
                                jobs_unchanged += 1
                        else:
                            # Create new internship
                            internship = Internship(
                                source_id=source.id,
                                company_id=company.id,
                                source_job_id=normalized.source_job_id,
                                title=normalized.title,
                                description=normalized.description,
                                location=normalized.location,
                                country=normalized.country,
                                remote_status=normalized.remote_status,
                                employment_type=normalized.employment_type,
                                duration_weeks=normalized.duration_weeks,
                                application_url=normalized.application_url,
                                source_url=normalized.source_url,
                                posted_at=datetime.fromisoformat(normalized.posted_at) if normalized.posted_at else None,
                                content_hash=content_hash,
                                raw_content=normalized.raw_content,
                                status="active",
                            )
                            db.add(internship)
                            jobs_new += 1

                    except Exception as e:
                        logger.error(f"Error processing job {raw_job.source_job_id}: {e}")
                        continue

                # Update crawl run
                duration_ms = int((time.monotonic() - start_time) * 1000)
                crawl_run.status = "completed"
                crawl_run.completed_at = datetime.now(timezone.utc)
                crawl_run.jobs_new = jobs_new
                crawl_run.jobs_updated = jobs_updated
                crawl_run.jobs_unchanged = jobs_unchanged
                crawl_run.duration_ms = duration_ms

                # Update source stats
                source.last_crawled_at = datetime.now(timezone.utc)
                source.last_success_at = datetime.now(timezone.utc)
                source.success_count += 1
                source.jobs_found_total += jobs_new

                await db.commit()
                logger.info(
                    f"Crawl {source.name}: {jobs_new} new, "
                    f"{jobs_updated} updated, {jobs_unchanged} unchanged "
                    f"({duration_ms}ms)"
                )

            except Exception as e:
                crawl_run.status = "failed"
                crawl_run.error = str(e)
                crawl_run.completed_at = datetime.now(timezone.utc)
                source.last_failure_at = datetime.now(timezone.utc)
                source.failure_count += 1
                await db.commit()
                logger.error(f"Crawl failed for {source.name}: {e}")

            finally:
                await adapter.close()

        except Exception as e:
            logger.error(f"Fatal crawl error for source {source_id}: {e}")
            await db.rollback()


async def crawl_all_sources():
    """Crawl all enabled sources that are due for a crawl."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(Source).where(
                Source.enabled == True,
                Source.automation_status == "supported",
            )
        )
        sources = result.scalars().all()

    for source in sources:
        # Check if it's time to crawl
        if source.last_crawled_at:
            elapsed = (datetime.now(timezone.utc) - source.last_crawled_at).total_seconds()
            if elapsed < source.crawl_frequency_minutes * 60:
                continue

        logger.info(f"Starting crawl for: {source.name}")
        await crawl_source(str(source.id))
        # Small delay between sources to be respectful
        await asyncio.sleep(2)


async def run_scheduler():
    """Main scheduler loop."""
    load_all_adapters()

    # Seed sources on first run
    async with async_session_factory() as db:
        from app.crawlers.seed_sources import seed_sources
        await seed_sources(db)
        await db.commit()

    logger.info("Worker scheduler started. Running initial crawl...")

    while True:
        try:
            await crawl_all_sources()
        except Exception as e:
            logger.error(f"Scheduler error: {e}")

        # Run digest cycle (sends emails to users who are due)
        try:
            async with async_session_factory() as db:
                from app.services.digest import run_digest_cycle
                await run_digest_cycle(db)
        except Exception as e:
            logger.error(f"Digest cycle error: {e}")

        # Wait before next cycle (5 minutes)
        await asyncio.sleep(300)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    asyncio.run(run_scheduler())
