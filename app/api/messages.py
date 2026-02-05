"""Message API endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.websocket_manager import manager
from app.models.user import User
from app.schemas.message import MessageListResponse, MessageResponse, MessageUpdate
from app.services.message_service import (
    delete_message,
    get_messages_paginated,
    update_message,
)

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("", response_model=MessageListResponse)
async def get_messages(
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
) -> MessageListResponse:
    """
    Get paginated message history.

    Args:
        limit: Maximum number of messages to return (1-100).
        cursor: Optional cursor timestamp for pagination.
        db: Database session.

    Returns:
        Paginated message list with next cursor.
    """
    messages, next_cursor = await get_messages_paginated(db, limit, cursor)

    # Convert to response format
    message_responses = [
        MessageResponse(
            id=msg.id,
            user_id=msg.user_id,
            username=msg.user.username,
            content=msg.content,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
            is_deleted=msg.is_deleted,
        )
        for msg in messages
    ]

    return MessageListResponse(
        messages=message_responses,
        next_cursor=next_cursor,
    )


@router.patch("/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: UUID,
    message_data: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Edit a message (user must own the message).

    Args:
        message_id: ID of message to edit.
        message_data: New message content.
        current_user: Authenticated user.
        db: Database session.

    Returns:
        Updated message.

    Raises:
        HTTPException: If message not found or unauthorized.
    """
    message = await update_message(
        db,
        message_id,
        current_user.id,
        message_data.content,
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or you don't have permission to edit it",
        )

    # Broadcast message edit to all connected users
    await manager.broadcast_to_all(
        {
            "event": "message_edited",
            "data": {
                "message_id": str(message.id),
                "content": message.content,
                "updated_at": message.updated_at.isoformat(),
            },
        }
    )

    return MessageResponse(
        id=message.id,
        user_id=message.user_id,
        username=message.user.username,
        content=message.content,
        created_at=message.created_at,
        updated_at=message.updated_at,
        is_deleted=message.is_deleted,
    )


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message_endpoint(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Soft delete a message (user must own the message).

    Args:
        message_id: ID of message to delete.
        current_user: Authenticated user.
        db: Database session.

    Raises:
        HTTPException: If message not found or unauthorized.
    """
    message = await delete_message(db, message_id, current_user.id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or you don't have permission to delete it",
        )

    # Broadcast message deletion to all connected users
    await manager.broadcast_to_all(
        {
            "event": "message_deleted",
            "data": {
                "message_id": str(message.id),
            },
        }
    )
