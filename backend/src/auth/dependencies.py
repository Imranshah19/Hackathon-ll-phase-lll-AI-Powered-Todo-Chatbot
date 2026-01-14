"""
FastAPI dependencies for authentication.

Provides reusable dependencies for:
- Extracting and validating JWT tokens
- Getting the current authenticated user
- Enforcing authentication on routes
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from src.auth.jwt import TokenPayload, verify_access_token
from src.db import get_session
from src.models.user import User

# =============================================================================
# Security Scheme
# =============================================================================

# HTTPBearer extracts the token from "Authorization: Bearer <token>" header
security = HTTPBearer(auto_error=False)


# =============================================================================
# Dependencies
# =============================================================================


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> TokenPayload:
    """
    Extract and validate JWT token from Authorization header.

    Args:
        credentials: Bearer token credentials from header

    Returns:
        TokenPayload: Decoded token data

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_user(
    token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """
    Get the current authenticated user from the database.

    Args:
        token_payload: Validated token data
        session: Database session

    Returns:
        User: The authenticated user entity

    Raises:
        HTTPException 401: If user no longer exists in database
    """
    user = session.exec(
        select(User).where(User.id == token_payload.user_id)
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_id(
    token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
) -> UUID:
    """
    Get the current user's ID without database lookup.

    Use this when you only need the user ID (e.g., for filtering queries).
    More efficient than get_current_user when you don't need the full user entity.

    Args:
        token_payload: Validated token data

    Returns:
        UUID: The authenticated user's ID
    """
    return token_payload.user_id


# Type aliases for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
DbSession = Annotated[Session, Depends(get_session)]


__all__ = [
    "get_token_payload",
    "get_current_user",
    "get_current_user_id",
    "CurrentUser",
    "CurrentUserId",
    "DbSession",
    "security",
]
