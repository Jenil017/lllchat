"""User API endpoints."""

from fastapi import APIRouter

from app.schemas.user import OnlineUser
from app.services.presence_service import get_presence_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/online", response_model=list[OnlineUser])
async def get_online_users() -> list[dict]:
    """
    Get list of currently online users.

    Returns:
        List of online users with id and username.
    """
    presence_service = get_presence_service()
    online_users = await presence_service.get_online_users()
    return online_users
