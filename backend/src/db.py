"""
Database configuration and session management.

Provides SQLModel engine creation and session dependency for FastAPI.
"""

import os
from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

# Database URL from environment, with fallback for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost:5432/todo_app"
)

# For SQLite testing (useful for unit tests without real DB)
SQLITE_TEST_URL = "sqlite:///./test.db"

# Engine configuration
# - echo=False in production, True for debugging SQL queries
# - pool_pre_ping=True to handle stale connections
_engine_kwargs: dict[str, Any] = {
    "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
    "pool_pre_ping": True,
}

# SQLite doesn't support some PostgreSQL features
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

# Create the database engine
engine = create_engine(DATABASE_URL, **_engine_kwargs)


def create_db_and_tables() -> None:
    """
    Create all database tables defined by SQLModel models.

    Should be called once at application startup.
    In production, prefer using Alembic migrations instead.
    """
    SQLModel.metadata.create_all(engine)


def drop_db_and_tables() -> None:
    """
    Drop all database tables.

    WARNING: This is destructive. Use only in tests or development.
    """
    SQLModel.metadata.drop_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Usage with FastAPI:
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            return session.exec(select(User)).all()

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session


def get_test_engine(test_db_url: str = SQLITE_TEST_URL) -> Any:
    """
    Create a test database engine (typically SQLite in-memory).

    Args:
        test_db_url: Database URL for testing

    Returns:
        SQLModel engine configured for testing
    """
    test_kwargs: dict[str, Any] = {"echo": False}
    if test_db_url.startswith("sqlite"):
        test_kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(test_db_url, **test_kwargs)


__all__ = [
    "DATABASE_URL",
    "engine",
    "create_db_and_tables",
    "drop_db_and_tables",
    "get_session",
    "get_test_engine",
]
