"""
Authentication utilities package.

Provides:
- Password hashing (Argon2id)
- JWT token creation and verification
- FastAPI authentication dependencies
"""

from src.auth.dependencies import (
    CurrentUser,
    CurrentUserId,
    DbSession,
    get_current_user,
    get_current_user_id,
    get_token_payload,
)
from src.auth.jwt import (
    TokenPayload,
    create_access_token,
    verify_access_token,
)
from src.auth.password import hash_password, verify_password

__all__ = [
    # Password utilities
    "hash_password",
    "verify_password",
    # JWT utilities
    "create_access_token",
    "verify_access_token",
    "TokenPayload",
    # Dependencies
    "get_token_payload",
    "get_current_user",
    "get_current_user_id",
    "CurrentUser",
    "CurrentUserId",
    "DbSession",
]
