"""OTP service for generating and verifying one-time passwords."""

import random
import string
from typing import Optional
from upstash_redis import Redis


class OTPService:
    """Service for managing OTP codes with Upstash Redis."""

    def __init__(self, redis_client: Redis):
        """Initialize OTP service with Redis client."""
        self.redis = redis_client
        self.otp_expiry = 300  # 5 minutes in seconds

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """
        Generate a random OTP code.

        Args:
            length: Length of OTP code (default 6)

        Returns:
            str: Random numeric OTP code
        """
        return "".join(random.choices(string.digits, k=length))

    async def store_otp(self, email: str, otp: str) -> bool:
        """
        Store OTP in Redis with expiration.

        Args:
            email: User email address
            otp: OTP code to store

        Returns:
            bool: True if stored successfully
        """
        try:
            key = f"otp:{email}"
            self.redis.setex(key, self.otp_expiry, otp)
            return True
        except Exception as e:
            print(f"Error storing OTP: {e}")
            return False

    async def verify_otp(self, email: str, otp: str) -> bool:
        """
        Verify OTP code for email.

        Args:
            email: User email address
            otp: OTP code to verify

        Returns:
            bool: True if OTP is valid and matches
        """
        try:
            key = f"otp:{email}"
            stored_otp = self.redis.get(key)

            if stored_otp is None:
                return False

            # Verify OTP matches
            if stored_otp == otp:
                # Delete OTP after successful verification
                self.redis.delete(key)
                return True

            return False

        except Exception as e:
            print(f"Error verifying OTP: {e}")
            return False

    async def delete_otp(self, email: str) -> bool:
        """
        Delete OTP for email.

        Args:
            email: User email address

        Returns:
            bool: True if deleted successfully
        """
        try:
            key = f"otp:{email}"
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting OTP: {e}")
            return False


# Global instance (initialized in main.py startup)
otp_service: Optional[OTPService] = None
