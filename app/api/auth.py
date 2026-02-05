"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import UserResponse
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Register a new user.

    Args:
        user_data: User registration data.
        db: Database session.

    Returns:
        Created user object.

    Raises:
        HTTPException: If email or username already exists.
    """
    try:
        user = await register_user(
            db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Login and receive JWT access token.

    Args:
        credentials: Login credentials.
        db: Database session.

    Returns:
        JWT access token.

    Raises:
        HTTPException: If credentials are invalid.
    """
    user = await authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)

    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current authenticated user information.

    Args:
        current_user: Authenticated user from JWT token.

    Returns:
        Current user object.
    """
    return current_user
