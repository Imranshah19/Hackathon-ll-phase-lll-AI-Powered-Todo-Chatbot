# Data Model: Data Schemas (Phase-2)

**Feature**: 005-data-schemas-phase2
**Date**: 2026-01-13
**Status**: Draft

## Entity Overview

```
┌─────────────────────────────────────────────────────────────┐
│                          User                                │
├─────────────────────────────────────────────────────────────┤
│ PK  id: UUID                                                 │
│     email: EmailStr (unique, not null)                       │
│     password_hash: str (not null, never exposed)             │
│     created_at: datetime (UTC, auto)                         │
│     updated_at: datetime (UTC, auto-update)                  │
├─────────────────────────────────────────────────────────────┤
│ 1:N → Task (cascade delete)                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ user_id (FK)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                          Task                                │
├─────────────────────────────────────────────────────────────┤
│ PK  id: UUID                                                 │
│ FK  user_id: UUID (not null, indexed)                        │
│     title: str (1-255 chars, not null)                       │
│     description: str | None (max 4000 chars)                 │
│     is_completed: bool (default: false)                      │
│     created_at: datetime (UTC, auto)                         │
│     updated_at: datetime (UTC, auto-update)                  │
├─────────────────────────────────────────────────────────────┤
│ N:1 → User                                                   │
└─────────────────────────────────────────────────────────────┘
```

## Entity Definitions

### User

Represents an authenticated user account.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | UUID v4 |
| email | EmailStr | UNIQUE, NOT NULL | RFC 5322 validated |
| password_hash | str | NOT NULL | Argon2id hash, never exposed in API |
| created_at | datetime | NOT NULL, DEFAULT now() | UTC timezone |
| updated_at | datetime | NOT NULL, auto-update | UTC timezone |

**Indexes**:
- `ix_user_email` (UNIQUE) on `email`

**Constraints**:
- Email must be valid format (Pydantic EmailStr)
- Email must be unique across all users
- Password hash is write-only (no read endpoint)

### Task

Represents a todo item owned by a user.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | UUID v4 |
| user_id | UUID | FK → User.id, NOT NULL | Cascade delete |
| title | str | NOT NULL, len 1-255 | Required |
| description | str \| None | NULL allowed, max 4000 | Optional |
| is_completed | bool | NOT NULL, DEFAULT false | Simple toggle |
| created_at | datetime | NOT NULL, DEFAULT now() | UTC timezone |
| updated_at | datetime | NOT NULL, auto-update | UTC timezone |

**Indexes**:
- `ix_task_user_id` on `user_id` (for efficient user task queries)

**Constraints**:
- Title minimum 1 character, maximum 255
- Description maximum 4000 characters (nullable)
- Foreign key to User with CASCADE DELETE

## Relationships

### User → Task (One-to-Many)

- One User can have zero or more Tasks
- Each Task belongs to exactly one User
- When User is deleted, all associated Tasks are deleted (CASCADE)
- Tasks are filtered by user_id for multi-tenant isolation

## SQLModel Implementation

### Base Models (Shared Validation)

```python
from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from uuid import UUID
from datetime import datetime

class UserBase(SQLModel):
    email: EmailStr

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    is_completed: bool = Field(default=False)
```

### Table Models (Database Entities)

```python
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)

    tasks: list["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Task(TaskBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)

    user: User | None = Relationship(back_populates="tasks")
```

### API Schemas (Request/Response)

```python
# Input schemas
class UserCreate(UserBase):
    password: str = Field(min_length=8)  # Plain password, will be hashed

class TaskCreate(TaskBase):
    pass  # user_id injected from auth context

class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    is_completed: bool | None = None

# Output schemas (never expose password_hash)
class UserPublic(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class TaskPublic(TaskBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
```

## Validation Rules

### User Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| email | Valid email format | "Invalid email format" |
| email | Unique in database | "Email already registered" |
| password | Min 8 characters | "Password must be at least 8 characters" |

### Task Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| title | Not empty | "Title is required" |
| title | Max 255 chars | "Title must not exceed 255 characters" |
| description | Max 4000 chars | "Description must not exceed 4000 characters" |
| user_id | Valid user exists | "User not found" |

## State Transitions

### Task Status

```
┌─────────────┐     toggle      ┌─────────────┐
│ is_completed│ ───────────────▶│ is_completed│
│   = false   │◀─────────────── │   = true    │
└─────────────┘     toggle      └─────────────┘
```

- Binary state only (no multi-state workflow in Phase-2)
- Any status change updates `updated_at` timestamp

## Database Migration Notes

### Initial Schema (PostgreSQL DDL)

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_email UNIQUE (email)
);

CREATE INDEX ix_user_email ON "user" (email);

-- Tasks table
CREATE TABLE task (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(4000),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_task_user FOREIGN KEY (user_id)
        REFERENCES "user" (id) ON DELETE CASCADE
);

CREATE INDEX ix_task_user_id ON task (user_id);
```

## Traceability

| Requirement | Implementation |
|-------------|----------------|
| FR-001 | User entity with id, email, password_hash, timestamps |
| FR-002 | Task entity with id, user_id, title, description, is_completed, timestamps |
| FR-003 | UNIQUE constraint on User.email |
| FR-004 | FOREIGN KEY on Task.user_id → User.id |
| FR-005 | UUID primary keys with uuid4() default |
| FR-006 | created_at with utc_now() default |
| FR-007 | updated_at auto-update on modification |
| FR-008 | EmailStr type for email validation |
| FR-009 | Field(min_length=1, max_length=255) on title |
| FR-010 | Field(max_length=4000) on description |
| FR-011 | password_hash excluded from UserPublic schema |
| FR-012 | CASCADE DELETE on User→Task relationship |
| FR-013 | Pydantic validation errors with field names |
| FR-014 | description: str \| None with default=None |
| FR-015 | datetime with timezone.utc |
