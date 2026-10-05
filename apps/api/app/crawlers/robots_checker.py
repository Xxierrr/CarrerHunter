"""
robots.txt Checker — Ethical crawling enforcement.

Checks robots.txt for each source before crawling to ensure we respect
site owners' wishes. Caches results to avoid repeated fetches.
"""

import logging
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

logger = logging.getLogger(__name__)

# In-memory cache: {domain: (RobotFileParser, timestamp)}
_robots_cache: dict[str, tuple[RobotFileParser, float]] = {}

# Cache TTL: 6 hours
CACHE_TTL_SECONDS = 6 * 3600

# Our bot user-agent
USER_AGENT = "InternshipIntel/1.0"


class RobotsChecker:
    """
    Checks robots.txt compliance before crawling a URL.

    Usage:
        checker = RobotsChecker()
        if await checker.can_fetch(url):
            # proceed with crawl
        else:
            # skip this URL
    """

    def __init__(self, user_agent: str = USER_AGENT):
        self.user_agent = user_agent

    def _get_robots_url(self, url: str) -> str:
        """Extract robots.txt URL from a given URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL for caching."""
        return urlparse(url).netloc

    async def _fetch_robots(self, url: str) -> RobotFileParser:
        """Fetch and parse robots.txt for a given URL."""
        robots_url = self._get_robots_url(url)
        domain = self._get_domain(url)

        # Check cache
        if domain in _robots_cache:
            parser, cached_at = _robots_cache[domain]
            if time.time() - cached_at < CACHE_TTL_SECONDS:
                return parser

        # Fetch robots.txt
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(robots_url)
                if response.status_code == 200:
                    parser.parse(response.text.splitlines())
                elif response.status_code in (404, 410):
                    # No robots.txt = everything allowed
                    parser.parse([])
                else:
                    # On error, be permissive but log
                    logger.warning(
                        f"robots.txt returned {response.status_code} for {domain}"
                    )
                    parser.parse([])
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt for {domain}: {e}")
            # On network error, allow crawling but note the failure
            parser.parse([])

        # Cache the result
        _robots_cache[domain] = (parser, time.time())
        return parser

    async def can_fetch(self, url: str) -> bool:
        """
        Check if our bot is allowed to fetch the given URL.
        Returns True if allowed, False if blocked by robots.txt.
        """
        try:
            parser = await self._fetch_robots(url)
            allowed = parser.can_fetch(self.user_agent, url)

            if not allowed:
                logger.info(f"robots.txt blocks crawling: {url}")

            return allowed
        except Exception as e:
            logger.error(f"robots.txt check failed for {url}: {e}")
            # On error, be cautious and allow (most ATS APIs are fine)
            return True

    async def get_crawl_delay(self, url: str) -> float | None:
        """
        Get the crawl-delay directive for a URL's domain, if specified.
        Returns delay in seconds, or None if not specified.
        """
        try:
            parser = await self._fetch_robots(url)
            delay = parser.crawl_delay(self.user_agent)
            return float(delay) if delay is not None else None
        except Exception:
            return None

    def clear_cache(self):
        """Clear the robots.txt cache."""
        _robots_cache.clear()

    def remove_from_cache(self, url: str):
        """Remove a specific domain from the cache."""
        domain = self._get_domain(url)
        _robots_cache.pop(domain, None)


# Module-level singleton
_checker: RobotsChecker | None = None


def get_robots_checker() -> RobotsChecker:
    """Get or create the singleton robots checker."""
    global _checker
    if _checker is None:
        _checker = RobotsChecker()
    return _checker
