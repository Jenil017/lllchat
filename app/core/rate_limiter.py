"""Redis-based rate limiter using sliding window algorithm."""

import time
from typing import Optional
from uuid import UUID

from upstash_redis import Redis

from app.core.config import settings


class RateLimiter:
    """
    Rate limiter using Redis sorted sets for sliding window tracking.

    Implements a sliding window algorithm to limit actions per time period.
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize rate limiter with Redis client.

        Args:
            redis_client: Upstash Redis client instance.
        """
        self.redis = redis_client
        self.window_size = 5  # seconds
        self.max_requests = 5  # maximum requests per window

    def _get_key(self, user_id: UUID, action: str) -> str:
        """
        Generate Redis key for rate limiting.

        Args:
            user_id: User's unique identifier.
            action: Action being rate limited (e.g., 'send_message').

        Returns:
            Redis key string.
        """
        return f"rate_limit:{action}:{user_id}"

    async def check_rate_limit(
        self, user_id: UUID, action: str = "send_message"
    ) -> bool:
        """
        Check if a user can perform an action within rate limits.

        Args:
            user_id: User's unique identifier.
            action: Action being rate limited.

        Returns:
            True if action is allowed, False if rate limit exceeded.
        """
        key = self._get_key(user_id, action)
        now = time.time()
        window_start = now - self.window_size

        # Remove old entries outside the window
        self.redis.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        request_count = self.redis.zcard(key)

        if request_count >= self.max_requests:
            return False

        # Add current request to the window
        self.redis.zadd(key, {str(now): now})

        # Set expiration to clean up old keys
        self.redis.expire(key, self.window_size * 2)

        return True

    async def reset_rate_limit(
        self, user_id: UUID, action: str = "send_message"
    ) -> None:
        """
        Reset rate limit for a user and action.

        Args:
            user_id: User's unique identifier.
            action: Action to reset rate limit for.
        """
        key = self._get_key(user_id, action)
        self.redis.delete(key)


# Global rate limiter instance (will be initialized in main.py)
rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Get the global rate limiter instance.

    Returns:
        RateLimiter instance.

    Raises:
        RuntimeError: If rate limiter is not initialized.
    """
    if rate_limiter is None:
        raise RuntimeError("Rate limiter not initialized")
    return rate_limiter
