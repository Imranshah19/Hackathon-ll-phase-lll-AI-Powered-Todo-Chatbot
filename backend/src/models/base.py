"""
Base model utilities and common imports for SQLModel entities.

This module provides:
- UTC timestamp helper function
- Common imports for all models
- Base configuration for SQLModel
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    pass

__all__ = [
    # Timestamp utilities
    "utc_now",
    # Re-exports for convenience
    "datetime",
    "timezone",
    "UUID",
    "uuid4",
    "EmailStr",
    "Field",
    "Relationship",
    "SQLModel",
]


def utc_now() -> datetime:
    """
    Generate current UTC timestamp with timezone awareness.

    Returns:
        datetime: Current time in UTC with tzinfo set to timezone.utc

    Example:
        >>> from src.models.base import utc_now
        >>> timestamp = utc_now()
        >>> assert timestamp.tzinfo == timezone.utc
    """
    return datetime.now(timezone.utc)
