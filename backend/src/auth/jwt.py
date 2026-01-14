"""
JWT token creation and verification.

Implements JWT-based authentication using python-jose.
Tokens are signed with HS256 algorithm using a shared secret.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

# =============================================================================
# Configuration
# =============================================================================

# Secret key for signing tokens - MUST be set in production
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


# =============================================================================
# Token Creation
# =============================================================================


def create_access_token(
    user_id: UUID,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: User's unique identifier
        email: User's email address
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token

    Example:
        >>> token = create_access_token(user_id, "user@example.com")
        >>> assert token.count(".") == 2  # JWT format: header.payload.signature
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


# =============================================================================
# Token Verification
# =============================================================================


class TokenPayload:
    """Decoded JWT token payload."""

    def __init__(self, user_id: UUID, email: str):
        self.user_id = user_id
        self.email = email


def verify_access_token(token: str) -> TokenPayload | None:
    """
    Verify and decode a JWT access token.

    Args:
        token: JWT token string

    Returns:
        TokenPayload if valid, None if invalid or expired

    Example:
        >>> token = create_access_token(user_id, "user@example.com")
        >>> payload = verify_access_token(token)
        >>> assert payload is not None
        >>> assert payload.email == "user@example.com"
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        # Validate required fields
        user_id_str = payload.get("sub")
        email = payload.get("email")
        token_type = payload.get("type")

        if not user_id_str or not email:
            return None

        if token_type != "access":
            return None

        return TokenPayload(
            user_id=UUID(user_id_str),
            email=email,
        )

    except JWTError:
        return None
    except ValueError:
        # Invalid UUID
        return None


__all__ = [
    "create_access_token",
    "verify_access_token",
    "TokenPayload",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
]
