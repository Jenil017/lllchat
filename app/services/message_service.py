"""Message service with business logic."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.message import Message
from app.models.user import User


async def create_message(
    db: AsyncSession,
    user_id: UUID,
    content: str,
) -> Message:
    """
    Create a new message.

    Args:
        db: Database session.
        user_id: ID of user creating the message.
        content: Message content.

    Returns:
        Created Message object with loaded user relationship.
    """
    message = Message(
        user_id=user_id,
        content=content,
    )

    db.add(message)
    await db.flush()
    await db.refresh(message, ["user"])

    return message


async def get_messages_paginated(
    db: AsyncSession,
    limit: int = 50,
    cursor: Optional[datetime] = None,
) -> tuple[list[Message], Optional[datetime]]:
    """
    Get paginated messages with cursor-based pagination.

    Args:
        db: Database session.
        limit: Maximum number of messages to return.
        cursor: Optional cursor timestamp for pagination.

    Returns:
        Tuple of (messages list, next cursor timestamp or None).
    """
    query = (
        select(Message)
        .options(joinedload(Message.user))
        .where(Message.is_deleted == False)
        .order_by(desc(Message.created_at))
        .limit(limit + 1)  # Fetch one extra to determine if there are more
    )

    if cursor:
        query = query.where(Message.created_at < cursor)

    result = await db.execute(query)
    messages = list(result.scalars().all())

    # Determine next cursor
    next_cursor = None
    if len(messages) > limit:
        messages = messages[:limit]
        next_cursor = messages[-1].created_at

    return messages, next_cursor


async def get_message_by_id(
    db: AsyncSession,
    message_id: UUID,
) -> Optional[Message]:
    """
    Get a message by ID.

    Args:
        db: Database session.
        message_id: Message unique identifier.

    Returns:
        Message object if found, None otherwise.
    """
    result = await db.execute(
        select(Message)
        .options(joinedload(Message.user))
        .where(Message.id == message_id)
    )
    return result.scalar_one_or_none()


async def update_message(
    db: AsyncSession,
    message_id: UUID,
    user_id: UUID,
    content: str,
) -> Optional[Message]:
    """
    Update a message (user must own the message).

    Args:
        db: Database session.
        message_id: Message ID to update.
        user_id: ID of user attempting to update.
        content: New message content.

    Returns:
        Updated Message object if successful, None if not found or unauthorized.
    """
    message = await get_message_by_id(db, message_id)

    if not message:
        return None

    # Authorization check: user must own the message
    if message.user_id != user_id:
        return None

    # Cannot edit deleted messages
    if message.is_deleted:
        return None

    message.content = content
    message.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(message)

    return message


async def delete_message(
    db: AsyncSession,
    message_id: UUID,
    user_id: UUID,
) -> Optional[Message]:
    """
    Soft delete a message (user must own the message).

    Args:
        db: Database session.
        message_id: Message ID to delete.
        user_id: ID of user attempting to delete.

    Returns:
        Deleted Message object if successful, None if not found or unauthorized.
    """
    message = await get_message_by_id(db, message_id)

    if not message:
        return None

    # Authorization check: user must own the message
    if message.user_id != user_id:
        return None

    # Already deleted
    if message.is_deleted:
        return None

    message.is_deleted = True

    await db.flush()
    await db.refresh(message)

    return message
