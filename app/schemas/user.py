"""User schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """Schema for user response data."""

    id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    last_seen: datetime | None
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class OnlineUser(BaseModel):
    """Schema for online user information."""

    id: UUID
    username: str

    model_config = {"from_attributes": True}
