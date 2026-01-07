"""
Rate Limiter Service
Implements token bucket algorithm for API rate limiting
"""

import logging
import time
from collections import deque
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter
    Tracks API calls and enforces rate limits
    """

    def __init__(self, max_calls: int, period: int = 60):
        """
        Initialize rate limiter

        Args:
            max_calls: Maximum number of calls allowed
            period: Time period in seconds (default: 60s)
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        logger.info(f"Rate limiter initialized: {max_calls} calls per {period}s")

    def can_proceed(self) -> bool:
        """
        Check if a new call can proceed

        Returns:
            True if call is allowed, False if rate limit exceeded
        """
        now = time.time()

        # Remove calls outside the time window
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()

        # Check if we're under the limit
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True

        logger.warning(
            f"⚠️ Rate limit exceeded: {len(self.calls)}/{self.max_calls} calls in last {self.period}s"
        )
        return False

    def remaining_calls(self) -> int:
        """
        Get number of remaining calls in current window

        Returns:
            Number of calls remaining
        """
        now = time.time()

        # Remove expired calls
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()

        return max(0, self.max_calls - len(self.calls))

    def time_until_reset(self) -> float:
        """
        Get time until rate limit resets

        Returns:
            Seconds until oldest call expires
        """
        if not self.calls:
            return 0.0

        now = time.time()
        oldest_call = self.calls[0]
        time_until_reset = max(0, self.period - (now - oldest_call))
        return time_until_reset

    def wait_if_needed(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until a call can proceed or timeout

        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)

        Returns:
            True if call can proceed, False if timed out
        """
        start_time = time.time()

        while not self.can_proceed():
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"Rate limiter timeout after {timeout}s")
                return False

            # Wait a bit before checking again
            time_to_wait = min(1.0, self.time_until_reset())
            time.sleep(time_to_wait)

        return True

    def reset(self):
        """Reset the rate limiter"""
        self.calls.clear()
        logger.info("Rate limiter reset")

    def get_status(self) -> dict:
        """
        Get current rate limiter status

        Returns:
            {
                "max_calls": int,
                "period": int,
                "remaining": int,
                "time_until_reset": float
            }
        """
        return {
            "max_calls": self.max_calls,
            "period": self.period,
            "remaining": self.remaining_calls(),
            "time_until_reset": self.time_until_reset(),
        }


class MultiRateLimiter:
    """
    Multiple rate limiters for different APIs
    """

    def __init__(self):
        """Initialize multi-rate limiter"""
        self.limiters = {}

    def add_limiter(self, name: str, max_calls: int, period: int = 60):
        """
        Add a rate limiter

        Args:
            name: Limiter name (e.g., "groq", "pubmed")
            max_calls: Maximum calls allowed
            period: Time period in seconds
        """
        self.limiters[name] = RateLimiter(max_calls, period)
        logger.info(f"Added rate limiter '{name}': {max_calls} calls per {period}s")

    def can_proceed(self, name: str) -> bool:
        """
        Check if call can proceed for specific limiter

        Args:
            name: Limiter name

        Returns:
            True if allowed, False if rate limited
        """
        if name not in self.limiters:
            logger.warning(f"No rate limiter found for '{name}'")
            return True

        return self.limiters[name].can_proceed()

    def wait_if_needed(self, name: str, timeout: Optional[float] = None) -> bool:
        """
        Wait for specific limiter

        Args:
            name: Limiter name
            timeout: Maximum wait time

        Returns:
            True if can proceed, False if timed out
        """
        if name not in self.limiters:
            return True

        return self.limiters[name].wait_if_needed(timeout)

    def get_status(self, name: Optional[str] = None) -> dict:
        """
        Get status of limiter(s)

        Args:
            name: Specific limiter name (None = all limiters)

        Returns:
            Status dict or dict of all statuses
        """
        if name:
            if name in self.limiters:
                return {name: self.limiters[name].get_status()}
            return {}

        return {name: limiter.get_status() for name, limiter in self.limiters.items()}


# Global rate limiter instance
_global_limiters = MultiRateLimiter()


def get_rate_limiter() -> MultiRateLimiter:
    """Get global rate limiter instance"""
    return _global_limiters


def initialize_rate_limiters():
    """Initialize all rate limiters with config from environment"""
    import os

    limiter = get_rate_limiter()

    # Groq API (30 requests/minute free tier)
    limiter.add_limiter(
        "groq", max_calls=int(os.getenv("GROQ_RATE_LIMIT", 30)), period=60
    )

    # PubMed API (3 requests/second recommended)
    limiter.add_limiter(
        "pubmed", max_calls=int(os.getenv("PUBMED_RATE_LIMIT", 3)), period=1
    )

    # Qdrant (no strict limit, but be reasonable)
    limiter.add_limiter(
        "qdrant", max_calls=int(os.getenv("QDRANT_RATE_LIMIT", 100)), period=60
    )

    logger.info("✅ All rate limiters initialized")


# Initialize on module import
try:
    initialize_rate_limiters()
except Exception as e:
    logger.warning(f"Failed to initialize rate limiters: {e}")
