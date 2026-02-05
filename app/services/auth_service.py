"""Authentication service with business logic."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Fetch a user by email address.

    Args:
        db: Database session.
        email: User's email address.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Fetch a user by username.

    Args:
        db: Database session.
        username: User's username.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Fetch a user by ID.

    Args:
        db: Database session.
        user_id: User's unique identifier.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def register_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
) -> User:
    """
    Register a new user.

    Args:
        db: Database session.
        username: Desired username.
        email: User's email address.
        password: Plain text password.

    Returns:
        Created User object.

    Raises:
        ValueError: If username or email already exists.
    """
    # Check if email already exists
    existing_email = await get_user_by_email(db, email)
    if existing_email:
        raise ValueError("Email already registered")

    # Check if username already exists
    existing_username = await get_user_by_username(db, username)
    if existing_username:
        raise ValueError("Username already taken")

    # Create new user with hashed password
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """
    Authenticate a user with email and password.

    Args:
        db: Database session.
        email: User's email address.
        password: Plain text password.

    Returns:
        User object if authentication succeeds, None otherwise.
    """
    user = await get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
