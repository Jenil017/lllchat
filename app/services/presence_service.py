"""Presence service using Upstash Redis REST API for online user tracking."""

from typing import Optional
from uuid import UUID
from upstash_redis import Redis


class PresenceService:
    """
    Service for tracking online users using Upstash Redis REST API.

    Uses Redis sets for efficient membership tracking.
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize presence service.

        Args:
            redis_client: Upstash Redis client instance.
        """
        self.redis = redis_client
        self.presence_key = "presence:online_users"
        self.user_data_prefix = "presence:user:"

    async def add_user_presence(self, user_id: UUID, username: str) -> None:
        """
        Mark a user as online.

        Args:
            user_id: User's unique identifier.
            username: User's username.
        """
        # Add user to online set
        self.redis.sadd(self.presence_key, str(user_id))

        # Store user data (username) with TTL
        user_key = f"{self.user_data_prefix}{user_id}"
        self.redis.set(user_key, username, ex=3600)  # 1 hour TTL

    async def remove_user_presence(self, user_id: UUID) -> None:
        """
        Mark a user as offline.

        Args:
            user_id: User's unique identifier.
        """
        # Remove from online set
        self.redis.srem(self.presence_key, str(user_id))

        # Remove user data
        user_key = f"{self.user_data_prefix}{user_id}"
        self.redis.delete(user_key)

    async def get_online_users(self) -> list[dict[str, str]]:
        """
        Get list of all online users.

        Returns:
            List of dictionaries with user_id and username.
        """
        # Get all online user IDs
        user_ids = self.redis.smembers(self.presence_key)

        online_users = []
        for user_id in user_ids:
            user_key = f"{self.user_data_prefix}{user_id}"
            username = self.redis.get(user_key)

            if username:
                online_users.append(
                    {
                        "id": user_id,
                        "username": username,
                    }
                )
            else:
                # Clean up stale entry
                self.redis.srem(self.presence_key, user_id)

        return online_users

    async def is_user_online(self, user_id: UUID) -> bool:
        """
        Check if a user is online.

        Args:
            user_id: User's unique identifier.

        Returns:
            True if user is online, False otherwise.
        """
        return self.redis.sismember(self.presence_key, str(user_id))


# Global presence service instance (will be initialized in main.py)
presence_service: Optional[PresenceService] = None


def get_presence_service() -> PresenceService:
    """
    Get the global presence service instance.

    Returns:
        PresenceService instance.

    Raises:
        RuntimeError: If presence service is not initialized.
    """
    if presence_service is None:
        raise RuntimeError("Presence service not initialized")
    return presence_service
