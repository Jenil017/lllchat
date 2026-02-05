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
    Register a new user and send OTP verification email.

    Args:
        user_data: User registration data.
        db: Database session.

    Returns:
        Created user object.

    Raises:
        HTTPException: If email or username already exists.
    """
    from app.services.otp_service import otp_service
    from app.services.email_service import email_service

    try:
        user = await register_user(
            db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )

        # Auto-send OTP email after registration
        otp_code = otp_service.generate_otp()
        await otp_service.store_otp(user.email, otp_code)
        email_service.send_otp_email(user.email, otp_code)

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

    Only verified users can login.

    Args:
        credentials: Login credentials.
        db: Database session.

    Returns:
        JWT access token.

    Raises:
        HTTPException: If credentials are invalid or email not verified.
    """
    user = await authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Check your inbox for OTP code.",
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


@router.post("/send-otp")
async def send_otp(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Send OTP verification code to email.

    Args:
        email: Email address to send OTP
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user not found or email sending fails
    """
    from app.services.auth_service import get_user_by_email
    from app.services.otp_service import otp_service
    from app.services.email_service import email_service

    # Check if user exists
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if already verified
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )

    # Generate and store OTP
    otp_code = otp_service.generate_otp()
    await otp_service.store_otp(email, otp_code)

    # Send OTP email
    email_sent = email_service.send_otp_email(email, otp_code)

    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email",
        )

    return {"message": "OTP sent successfully", "email": email}


@router.post("/verify-otp")
async def verify_otp(
    email: str,
    otp: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify OTP code and mark user as verified.

    Args:
        email: Email address
        otp: 6-digit OTP code
        db: Database session

    Returns:
        Success message and token

    Raises:
        HTTPException: If OTP is invalid or user not found
    """
    from app.services.auth_service import get_user_by_email, mark_user_verified
    from app.services.otp_service import otp_service

    # Verify OTP
    is_valid = await otp_service.verify_otp(email, otp)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    # Get user
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Mark user as verified
    await mark_user_verified(db, user.id)

    # Generate access token
    access_token = create_access_token(user.id)

    return {
        "message": "Email verified successfully",
        "verified": True,
        "access_token": access_token,
        "token_type": "bearer",
    }
