"""
Alembic migration environment configuration.

Configured for SQLModel with environment-based database URL.
"""

import os
from logging.config import fileConfig

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Import all models to register them with SQLModel.metadata
# Phase 2 models
from src.models.task import Task
from src.models.user import User
# Phase 3 models
from src.models.conversation import Conversation
from src.models.message import Message

# Alembic Config object
config = context.config

# Override sqlalchemy.url from environment variable
# Default to SQLite for local development
database_url = os.getenv(
    "DATABASE_URL",
    "sqlite:///./dev.db"
)
config.set_main_option("sqlalchemy.url", database_url)

# Python logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel metadata for autogenerate support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Generates SQL script without database connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Connects to database and applies migrations.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
