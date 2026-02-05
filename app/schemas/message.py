"""Message schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    content: str = Field(..., min_length=1, max_length=2000)


class MessageUpdate(BaseModel):
    """Schema for updating a message."""

    content: str = Field(..., min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    """Schema for message response data."""

    id: UUID
    user_id: UUID
    username: str
    content: str
    created_at: datetime
    updated_at: datetime | None
    is_deleted: bool

    model_config = {"from_attributes": True}


class MessageListResponse(BaseModel):
    """Schema for paginated message list response."""

    messages: list[MessageResponse]
    next_cursor: datetime | None
