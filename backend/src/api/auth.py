"""
Authentication API routes.

Endpoints:
- POST /api/auth/register - Create new user account
- POST /api/auth/login - Authenticate and get JWT token
- GET /api/auth/me - Get current user profile
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from src.auth.dependencies import CurrentUser, DbSession
from src.auth.jwt import create_access_token
from src.auth.password import hash_password, verify_password
from src.models.user import User, UserCreate, UserPublic

router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================


class LoginRequest(BaseModel):
    """Login credentials."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Registration response with user and token."""

    user: UserPublic
    access_token: str
    token_type: str = "bearer"


# =============================================================================
# Routes
# =============================================================================


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_data: UserCreate,
    session: DbSession,
) -> RegisterResponse:
    """
    Create a new user account.

    - Validates email format and password length
    - Checks for duplicate email
    - Hashes password with Argon2id
    - Returns user profile and JWT token
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user with hashed password
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate access token
    access_token = create_access_token(
        user_id=user.id,  # type: ignore
        email=user.email,
    )

    return RegisterResponse(
        user=UserPublic.model_validate(user),
        access_token=access_token,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get access token",
)
async def login(
    credentials: LoginRequest,
    session: DbSession,
) -> TokenResponse:
    """
    Authenticate user and return JWT token.

    - Validates credentials against database
    - Returns 401 for invalid email or password
    - Returns JWT access token on success
    """
    # Find user by email
    user = session.exec(
        select(User).where(User.email == credentials.email)
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(user.password_hash, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate access token
    access_token = create_access_token(
        user_id=user.id,  # type: ignore
        email=user.email,
    )

    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get current user profile",
)
async def get_me(current_user: CurrentUser) -> UserPublic:
    """
    Get the authenticated user's profile.

    Requires valid JWT token in Authorization header.
    """
    return UserPublic.model_validate(current_user)


__all__ = ["router"]
