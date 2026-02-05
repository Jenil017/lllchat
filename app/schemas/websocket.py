"""WebSocket event schemas."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class WSMessage(BaseModel):
    """Base WebSocket message structure."""

    event: str
    data: dict[str, Any]


# Client → Server Events


class SendMessageEvent(BaseModel):
    """Client sends a new message."""

    event: Literal["send_message"] = "send_message"
    data: dict[str, str]  # {"content": "message text"}


class TypingEvent(BaseModel):
    """Client is typing."""

    event: Literal["typing"] = "typing"
    data: dict[str, Any] = {}


class PingEvent(BaseModel):
    """Client sends ping."""

    event: Literal["ping"] = "ping"
    data: dict[str, Any] = {}


# Server → Client Events


class NewMessageEvent(BaseModel):
    """Server broadcasts new message."""

    event: Literal["new_message"] = "new_message"
    data: dict[str, Any]  # Complete message object


class MessageEditedEvent(BaseModel):
    """Server broadcasts message edit."""

    event: Literal["message_edited"] = "message_edited"
    data: dict[str, Any]  # {"message_id": UUID, "content": str, "updated_at": datetime}


class MessageDeletedEvent(BaseModel):
    """Server broadcasts message deletion."""

    event: Literal["message_deleted"] = "message_deleted"
    data: dict[str, UUID]  # {"message_id": UUID}


class UserJoinedEvent(BaseModel):
    """Server broadcasts user joined."""

    event: Literal["user_joined"] = "user_joined"
    data: dict[str, Any]  # {"user_id": UUID, "username": str}


class UserLeftEvent(BaseModel):
    """Server broadcasts user left."""

    event: Literal["user_left"] = "user_left"
    data: dict[str, Any]  # {"user_id": UUID, "username": str}


class UserTypingEvent(BaseModel):
    """Server broadcasts typing indicator."""

    event: Literal["user_typing"] = "user_typing"
    data: dict[str, Any]  # {"user_id": UUID, "username": str}


class PongEvent(BaseModel):
    """Server responds to ping."""

    event: Literal["pong"] = "pong"
    data: dict[str, Any] = {}
