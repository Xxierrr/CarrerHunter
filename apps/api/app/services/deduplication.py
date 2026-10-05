"""
Deduplication Engine.

Multi-level deduplication to prevent showing the same internship multiple times:
1. Exact source_job_id match
2. Canonical application URL
3. Company + normalized title + location
4. Content hash similarity
"""

import hashlib
import re
import logging
from urllib.parse import urlparse, urljoin

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.internship import Internship

logger = logging.getLogger(__name__)


def normalize_title(title: str) -> str:
    """Normalize job title for comparison."""
    title = title.lower().strip()
    # Remove common suffixes/prefixes
    title = re.sub(r'\s*[-–—|]\s*(intern|internship|co-op)', '', title)
    title = re.sub(r'\s*\(.*?\)', '', title)  # Remove parenthetical
    title = re.sub(r'\s+', ' ', title)  # Collapse whitespace
    return title.strip()


def normalize_company(name: str) -> str:
    """Normalize company name for comparison."""
    name = name.lower().strip()
    # Remove common suffixes
    for suffix in [" inc", " inc.", " corp", " corp.", " ltd", " llc", " co.", " company"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name.strip()


def normalize_url(url: str | None) -> str | None:
    """Normalize a URL for comparison."""
    if not url:
        return None
    parsed = urlparse(url)
    # Remove tracking parameters
    clean_path = parsed.path.rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}{clean_path}".lower()


def compute_content_hash(content: str | None) -> str:
    """Compute SHA-256 hash of content for change detection."""
    if not content:
        return ""
    # Normalize whitespace before hashing
    normalized = re.sub(r'\s+', ' ', content.strip())
    return hashlib.sha256(normalized.encode()).hexdigest()


async def find_duplicate(
    db: AsyncSession,
    source_id: str | None,
    source_job_id: str,
    company_name: str,
    title: str,
    location: str | None,
    application_url: str | None,
    content_hash: str | None,
) -> Internship | None:
    """
    Check for duplicate internship using multi-level matching.
    Returns the existing internship if found, None otherwise.
    """

    # Level 1: Exact source_job_id match from same source
    if source_id and source_job_id:
        result = await db.execute(
            select(Internship).where(
                Internship.source_id == source_id,
                Internship.source_job_id == source_job_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    # Level 2: Canonical application URL
    if application_url:
        norm_url = normalize_url(application_url)
        if norm_url:
            result = await db.execute(
                select(Internship).where(
                    Internship.application_url.ilike(f"%{urlparse(norm_url).path}%")
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing

    # Level 3: Company + normalized title + location
    norm_title = normalize_title(title)
    norm_company = normalize_company(company_name)
    if norm_title and norm_company:
        # Query with ILIKE for fuzzy matching
        result = await db.execute(
            select(Internship).where(
                Internship.title.ilike(f"%{norm_title[:50]}%"),
                Internship.status == "active",
            )
        )
        candidates = result.scalars().all()

        for candidate in candidates:
            from app.models.internship import Company
            if candidate.company_id:
                comp_result = await db.execute(
                    select(Company).where(Company.id == candidate.company_id)
                )
                comp = comp_result.scalar_one_or_none()
                if comp and normalize_company(comp.name) == norm_company:
                    # Same company + similar title = likely duplicate
                    candidate_norm_title = normalize_title(candidate.title)
                    if candidate_norm_title == norm_title:
                        return candidate

    # Level 4: Content hash match
    if content_hash:
        result = await db.execute(
            select(Internship).where(
                Internship.content_hash == content_hash,
                Internship.status == "active",
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    return None


def classify_change(old_hash: str | None, new_hash: str | None) -> str:
    """
    Classify the type of change between two content hashes.
    Returns: NO_CHANGE, MINOR_CHANGE, IMPORTANT_CHANGE, CLOSED
    """
    if not old_hash or not new_hash:
        return "IMPORTANT_CHANGE"
    if old_hash == new_hash:
        return "NO_CHANGE"
    # Without semantic comparison, any hash change is treated as important
    return "IMPORTANT_CHANGE"
