"""
Admin API routes — source management, AI usage, system stats.
Requires admin privileges.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone

from app.api.deps import AdminUser, DbSession
from app.models.internship import Internship, Source, Company
from app.models.system import CrawlRun, AIRequest, AICache
from app.models.user import User
from app.models.notification import EmailLog
from app.services.ai.gemini import get_ai_provider

router = APIRouter()


@router.get("/stats")
async def get_system_stats(admin: AdminUser, db: DbSession):
    """Get overall system statistics."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Users
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0

    # Internships
    total_internships = (await db.execute(
        select(func.count(Internship.id))
    )).scalar() or 0

    active_internships = (await db.execute(
        select(func.count(Internship.id)).where(Internship.status == "active")
    )).scalar() or 0

    new_today = (await db.execute(
        select(func.count(Internship.id)).where(Internship.created_at >= today_start)
    )).scalar() or 0

    # Sources
    total_sources = (await db.execute(select(func.count(Source.id)))).scalar() or 0
    enabled_sources = (await db.execute(
        select(func.count(Source.id)).where(Source.enabled == True)
    )).scalar() or 0

    # Companies
    total_companies = (await db.execute(select(func.count(Company.id)))).scalar() or 0

    return {
        "users": {"total": total_users},
        "internships": {
            "total": total_internships,
            "active": active_internships,
            "new_today": new_today,
        },
        "sources": {
            "total": total_sources,
            "enabled": enabled_sources,
        },
        "companies": {"total": total_companies},
    }


@router.get("/sources")
async def list_sources(admin: AdminUser, db: DbSession):
    """List all configured sources with their health status."""
    result = await db.execute(
        select(Source).order_by(Source.priority, Source.name)
    )
    sources = result.scalars().all()

    items = []
    for source in sources:
        # Determine health
        if source.last_failure_at and source.last_success_at:
            if source.last_failure_at > source.last_success_at:
                health = "failing"
            else:
                health = "healthy"
        elif source.last_success_at:
            health = "healthy"
        elif source.last_failure_at:
            health = "failing"
        else:
            health = "unknown"

        items.append({
            "id": str(source.id),
            "name": source.name,
            "type": source.type,
            "adapter_name": source.adapter_name,
            "automation_status": source.automation_status,
            "enabled": source.enabled,
            "priority": source.priority,
            "health": health,
            "last_crawled_at": source.last_crawled_at.isoformat() if source.last_crawled_at else None,
            "last_success_at": source.last_success_at.isoformat() if source.last_success_at else None,
            "last_failure_at": source.last_failure_at.isoformat() if source.last_failure_at else None,
            "success_count": source.success_count,
            "failure_count": source.failure_count,
            "jobs_found_total": source.jobs_found_total,
            "crawl_frequency_minutes": source.crawl_frequency_minutes,
        })

    return items


@router.get("/ai-usage")
async def get_ai_usage(admin: AdminUser, db: DbSession):
    """Get AI usage statistics."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Today's requests
    total_today = (await db.execute(
        select(func.count(AIRequest.id)).where(AIRequest.created_at >= today_start)
    )).scalar() or 0

    successful_today = (await db.execute(
        select(func.count(AIRequest.id)).where(
            AIRequest.created_at >= today_start,
            AIRequest.status == "success",
        )
    )).scalar() or 0

    cached_today = (await db.execute(
        select(func.count(AIRequest.id)).where(
            AIRequest.created_at >= today_start,
            AIRequest.cached == True,
        )
    )).scalar() or 0

    failed_today = (await db.execute(
        select(func.count(AIRequest.id)).where(
            AIRequest.created_at >= today_start,
            AIRequest.status == "failed",
        )
    )).scalar() or 0

    # Cache stats
    total_cache_entries = (await db.execute(
        select(func.count(AICache.id))
    )).scalar() or 0

    # Rate limiter stats
    provider = get_ai_provider()
    rate_stats = await provider.get_usage_stats()

    cache_hit_rate = (cached_today / total_today * 100) if total_today > 0 else 0

    return {
        "today": {
            "total_requests": total_today,
            "successful": successful_today,
            "cached": cached_today,
            "failed": failed_today,
            "cache_hit_rate": round(cache_hit_rate, 1),
        },
        "cache": {
            "total_entries": total_cache_entries,
        },
        "rate_limiter": rate_stats.get("rate_limiter", {}),
    }


@router.get("/crawl-runs")
async def get_crawl_runs(admin: AdminUser, db: DbSession, limit: int = 20):
    """Get recent crawl run history."""
    result = await db.execute(
        select(CrawlRun)
        .order_by(CrawlRun.started_at.desc())
        .limit(limit)
    )
    runs = result.scalars().all()

    items = []
    for run in runs:
        # Get source name
        source_name = None
        if run.source_id:
            source_result = await db.execute(
                select(Source.name).where(Source.id == run.source_id)
            )
            source_name = source_result.scalar_one_or_none()

        items.append({
            "id": str(run.id),
            "source_name": source_name,
            "status": run.status,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "jobs_found": run.jobs_found,
            "jobs_new": run.jobs_new,
            "jobs_updated": run.jobs_updated,
            "jobs_unchanged": run.jobs_unchanged,
            "error": run.error,
            "duration_ms": run.duration_ms,
        })

    return items
