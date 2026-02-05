"""WebSocket API endpoint for realtime chat."""

import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.rate_limiter import get_rate_limiter
from app.core.security import decode_access_token
from app.core.websocket_manager import manager
from app.models.user import User
from app.schemas.message import MessageResponse
from app.services.auth_service import get_user_by_id
from app.services.message_service import create_message
from app.services.presence_service import get_presence_service

router = APIRouter(tags=["WebSocket"])

logger = logging.getLogger(__name__)


async def get_user_from_token(token: str, db: AsyncSession) -> Optional[User]:
    """
    Validate JWT token and get user.

    Args:
        token: JWT token string.
        db: Database session.

    Returns:
        User object if valid, None otherwise.
    """
    user_id = decode_access_token(token)
    if not user_id:
        return None

    user = await get_user_by_id(db, user_id)
    return user


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    """
    WebSocket endpoint for realtime chat.

    Args:
        websocket: WebSocket connection.
        token: JWT authentication token from query parameter.
    """
    # Authenticate user
    async with async_session_maker() as db:
        user = await get_user_from_token(token, db)

        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        if not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    # Accept WebSocket connection
    await websocket.accept()

    # Add user to connection manager
    await manager.connect(user.id, websocket)

    # Add user to presence
    presence_service = get_presence_service()
    await presence_service.add_user_presence(user.id, user.username)

    # Broadcast user joined
    await manager.broadcast_to_all(
        {
            "event": "user_joined",
            "data": {
                "user_id": str(user.id),
                "username": user.username,
            },
        },
        exclude=user.id,
    )

    logger.info(f"User {user.username} ({user.id}) connected")

    try:
        # Main message handling loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            event = data.get("event")
            event_data = data.get("data", {})

            if event == "send_message":
                await handle_send_message(user, event_data)

            elif event == "typing":
                await handle_typing(user)

            elif event == "ping":
                await websocket.send_json(
                    {
                        "event": "pong",
                        "data": {},
                    }
                )

            else:
                logger.warning(f"Unknown event: {event}")

    except WebSocketDisconnect:
        logger.info(f"User {user.username} ({user.id}) disconnected")

    except Exception as e:
        logger.error(f"Error in WebSocket for user {user.username}: {e}")

    finally:
        # Cleanup on disconnect
        await manager.disconnect(user.id)
        await presence_service.remove_user_presence(user.id)

        # Broadcast user left
        await manager.broadcast_to_all(
            {
                "event": "user_left",
                "data": {
                    "user_id": str(user.id),
                    "username": user.username,
                },
            }
        )


async def handle_send_message(user: User, data: dict) -> None:
    """
    Handle send_message event from client.

    Args:
        user: Authenticated user.
        data: Event data containing message content.
    """
    content = data.get("content", "").strip()

    # Validate message content
    if not content:
        return

    if len(content) > 2000:
        await manager.send_to_user(
            user.id,
            {
                "event": "error",
                "data": {
                    "message": "Message exceeds 2000 character limit",
                },
            },
        )
        return

    # Check rate limit
    rate_limiter = get_rate_limiter()
    is_allowed = await rate_limiter.check_rate_limit(user.id, "send_message")

    if not is_allowed:
        await manager.send_to_user(
            user.id,
            {
                "event": "error",
                "data": {
                    "message": "Rate limit exceeded. Please slow down.",
                },
            },
        )
        return

    # Save message to database
    async with async_session_maker() as db:
        try:
            message = await create_message(db, user.id, content)
            await db.commit()

            # Broadcast new message to all users
            message_response = MessageResponse(
                id=message.id,
                user_id=message.user_id,
                username=user.username,
                content=message.content,
                created_at=message.created_at,
                updated_at=message.updated_at,
                is_deleted=message.is_deleted,
            )

            await manager.broadcast_to_all(
                {
                    "event": "new_message",
                    "data": message_response.model_dump(mode="json"),
                }
            )

        except Exception as e:
            logger.error(f"Error creating message: {e}")
            await db.rollback()


async def handle_typing(user: User) -> None:
    """
    Handle typing event from client.

    Args:
        user: Authenticated user.
    """
    # Broadcast typing indicator to all other users
    await manager.broadcast_to_all(
        {
            "event": "user_typing",
            "data": {
                "user_id": str(user.id),
                "username": user.username,
            },
        },
        exclude=user.id,
    )
