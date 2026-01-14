# Quickstart: Data Schemas (Phase-2)

**Feature**: 005-data-schemas-phase2
**Date**: 2026-01-13

## Overview

This document provides quick reference for implementing and using the Data Schemas feature.

## Prerequisites

- Python 3.11+
- PostgreSQL (Neon Serverless)
- Dependencies installed: `sqlmodel`, `pydantic`, `argon2-cffi`, `email-validator`

## Installation

```bash
# Install required packages
pip install sqlmodel argon2-cffi "pydantic[email]"
```

## Quick Implementation

### 1. Define Models

```python
# backend/src/models/user.py
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from uuid import UUID, uuid4
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class UserBase(SQLModel):
    email: EmailStr

class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    tasks: list["Task"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
```

```python
# backend/src/models/task.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    is_completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    user: "User" = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    is_completed: bool | None = None

class TaskPublic(TaskBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
```

### 2. Password Hashing

```python
# backend/src/auth/password.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hash: str, password: str) -> bool:
    try:
        ph.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False
```

### 3. Database Setup

```python
# backend/src/db.py
from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

## Usage Examples

### Create User

```python
from models.user import User, UserCreate
from auth.password import hash_password

user_create = UserCreate(email="user@example.com", password="securepass123")
user = User(
    email=user_create.email,
    password_hash=hash_password(user_create.password)
)
session.add(user)
session.commit()
```

### Create Task

```python
from models.task import Task, TaskCreate

task_create = TaskCreate(title="Buy groceries", description="Milk, eggs")
task = Task(
    **task_create.model_dump(),
    user_id=current_user.id
)
session.add(task)
session.commit()
```

### Query User's Tasks

```python
from sqlmodel import select

statement = select(Task).where(Task.user_id == current_user.id)
tasks = session.exec(statement).all()
```

### Update Task

```python
from models.task import TaskUpdate
from datetime import datetime, timezone

task_update = TaskUpdate(is_completed=True)
for key, value in task_update.model_dump(exclude_unset=True).items():
    setattr(task, key, value)
task.updated_at = datetime.now(timezone.utc)
session.add(task)
session.commit()
```

## Validation Examples

### Valid Inputs

```python
# Valid user
UserCreate(email="user@example.com", password="password123")  # OK

# Valid task
TaskCreate(title="A", description=None)  # OK (minimum title)
TaskCreate(title="Buy groceries", description="Long description...")  # OK
```

### Invalid Inputs

```python
# Invalid email
UserCreate(email="not-an-email", password="password123")
# → ValidationError: value is not a valid email address

# Empty title
TaskCreate(title="", description="Details")
# → ValidationError: String should have at least 1 character

# Title too long
TaskCreate(title="x" * 256, description=None)
# → ValidationError: String should have at most 255 characters

# Description too long
TaskCreate(title="Task", description="x" * 4001)
# → ValidationError: String should have at most 4000 characters
```

## Testing

```bash
# Run tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend/src/models
```

## Files Created

| File | Purpose |
|------|---------|
| `backend/src/models/user.py` | User entity and schemas |
| `backend/src/models/task.py` | Task entity and schemas |
| `backend/src/models/__init__.py` | Model exports |
| `backend/src/auth/password.py` | Password hashing utilities |
| `backend/tests/unit/test_models.py` | Unit tests for models |
| `backend/tests/contract/test_schemas.py` | Schema validation tests |

## Related Documents

- [Spec](./spec.md) - Feature requirements
- [Data Model](./data-model.md) - Entity definitions
- [API Contract](./contracts/openapi.yaml) - OpenAPI specification
- [Research](./research.md) - Technology decisions
