"""
Rate limiter and quota manager for Gemini free tier.
Tracks RPM, RPD, and provides backoff on quota exhaustion.
"""

import asyncio
import time
from collections import deque
from datetime import datetime, timezone


class RateLimiter:
    """
    Rate limiter for Gemini API free tier.
    Tracks:
    - Requests Per Minute (RPM)
    - Requests Per Day (RPD)
    Provides async waiting when limits are approached.
    """

    def __init__(self, rpm_limit: int = 14, daily_limit: int = 1400):
        self.rpm_limit = rpm_limit
        self.daily_limit = daily_limit

        # Track request timestamps
        self._minute_window: deque[float] = deque()
        self._daily_count: int = 0
        self._daily_reset_date: str = ""

        # Backoff tracking
        self._consecutive_failures: int = 0
        self._last_rate_limit_time: float = 0

    def _clean_minute_window(self):
        """Remove timestamps older than 60 seconds."""
        now = time.monotonic()
        while self._minute_window and (now - self._minute_window[0]) > 60:
            self._minute_window.popleft()

    def _check_daily_reset(self):
        """Reset daily counter if it's a new day (PT timezone ~ UTC-7/8)."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self._daily_reset_date:
            self._daily_count = 0
            self._daily_reset_date = today

    @property
    def requests_remaining_today(self) -> int:
        self._check_daily_reset()
        return max(0, self.daily_limit - self._daily_count)

    @property
    def requests_remaining_minute(self) -> int:
        self._clean_minute_window()
        return max(0, self.rpm_limit - len(self._minute_window))

    @property
    def is_available(self) -> bool:
        """Check if we can make a request right now."""
        return self.requests_remaining_today > 0 and self.requests_remaining_minute > 0

    async def acquire(self) -> bool:
        """
        Acquire permission to make a request.
        Waits if necessary (up to RPM cooldown).
        Returns False if daily limit is exhausted.
        """
        self._check_daily_reset()

        # Check daily limit
        if self._daily_count >= self.daily_limit:
            return False

        # Wait for RPM availability
        self._clean_minute_window()
        if len(self._minute_window) >= self.rpm_limit:
            # Wait until the oldest request falls out of the window
            oldest = self._minute_window[0]
            wait_time = 60 - (time.monotonic() - oldest) + 0.5
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self._clean_minute_window()

        # Record this request
        self._minute_window.append(time.monotonic())
        self._daily_count += 1
        return True

    def record_success(self):
        """Record a successful request (reset backoff)."""
        self._consecutive_failures = 0

    def record_failure(self, is_rate_limit: bool = False):
        """Record a failed request."""
        self._consecutive_failures += 1
        if is_rate_limit:
            self._last_rate_limit_time = time.monotonic()

    async def backoff_wait(self) -> float:
        """Exponential backoff wait. Returns time waited."""
        if self._consecutive_failures == 0:
            return 0

        wait_time = min(2 ** self._consecutive_failures, 60)  # Max 60s
        await asyncio.sleep(wait_time)
        return wait_time

    def get_stats(self) -> dict:
        """Get current rate limiter statistics."""
        self._check_daily_reset()
        self._clean_minute_window()
        return {
            "rpm_used": len(self._minute_window),
            "rpm_limit": self.rpm_limit,
            "rpm_remaining": self.requests_remaining_minute,
            "daily_used": self._daily_count,
            "daily_limit": self.daily_limit,
            "daily_remaining": self.requests_remaining_today,
            "consecutive_failures": self._consecutive_failures,
            "is_available": self.is_available,
        }
