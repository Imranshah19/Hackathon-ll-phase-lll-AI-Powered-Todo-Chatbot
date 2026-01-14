# Research: Data Schemas (Phase-2)

**Feature**: 005-data-schemas-phase2
**Date**: 2026-01-13
**Status**: Complete

## Overview

Research findings for implementing core data schemas (User, Task) in the Todo Full-Stack Web Application Phase-2.

## Technology Decisions

### 1. ORM Framework: SQLModel

**Decision**: Use SQLModel for all database models

**Rationale**:
- Combines Pydantic validation with SQLAlchemy ORM
- Type-safe Python models with automatic validation
- Seamless integration with FastAPI
- Single model definition serves both API schema and database entity
- Constitution mandates SQLModel (see §Technology Stack)

**Alternatives Considered**:
- SQLAlchemy Core: Lower level, more boilerplate, less type safety
- Django ORM: Would require Django framework, not compatible with FastAPI
- Tortoise ORM: Less mature, smaller ecosystem

### 2. Primary Key Strategy: UUID

**Decision**: Use UUID v4 for all primary keys

**Rationale**:
- Globally unique without coordination
- No sequential enumeration attacks
- Safe for distributed systems
- Spec requirement (FR-005): "System MUST auto-generate UUID for all entity IDs"

**Alternatives Considered**:
- Auto-increment integers: Sequential, predictable, coordination required
- ULID: Sortable but less standard library support
- Snowflake IDs: Overkill for this scale

### 3. Timestamp Handling: UTC with TZ-aware

**Decision**: Store all timestamps in UTC, use `datetime` with timezone awareness

**Rationale**:
- Spec requirement (FR-015): "System MUST store all timestamps in UTC"
- Avoids ambiguity in distributed systems
- Client-side conversion for display
- PostgreSQL `TIMESTAMP WITH TIME ZONE` provides native support

**Implementation Pattern**:
```python
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)
```

### 4. Password Storage: Argon2id

**Decision**: Use Argon2id for password hashing

**Rationale**:
- Winner of Password Hashing Competition (PHC)
- Memory-hard (resistant to GPU attacks)
- Recommended by OWASP
- Better than bcrypt for new implementations

**Alternatives Considered**:
- bcrypt: Still secure but Argon2 is newer standard
- PBKDF2: Less resistant to GPU attacks
- scrypt: Good but Argon2 has better security margin

### 5. Email Validation: Pydantic EmailStr

**Decision**: Use Pydantic's `EmailStr` type for email validation

**Rationale**:
- Built into Pydantic (already a dependency via SQLModel)
- RFC 5322 compliant validation
- No additional dependencies
- Spec requirement (FR-008): "System MUST validate User.email matches standard email format"

### 6. Field Length Constraints

**Decision**: Implement at both model and database level

**Rationale**:
- Model-level: Immediate feedback, type safety
- Database-level: Data integrity, defense in depth
- Spec requirements:
  - FR-009: Task.title 1-255 characters
  - FR-010: Task.description max 4000 characters

**Implementation Pattern**:
```python
from sqlmodel import Field
from pydantic import constr

title: str = Field(min_length=1, max_length=255)
description: str | None = Field(default=None, max_length=4000)
```

## Best Practices Applied

### SQLModel Entity Design

1. **Separate table models from API schemas**:
   - `UserBase`: Shared fields for validation
   - `User`: Database table model (includes password_hash)
   - `UserCreate`: API input schema (includes password, not hash)
   - `UserPublic`: API output schema (excludes sensitive fields)

2. **Use `table=True` only on database models**

3. **Define relationships explicitly**:
   ```python
   tasks: list["Task"] = Relationship(back_populates="user", cascade_delete=True)
   ```

### Validation Patterns

1. **Fail fast**: Validate at API boundary before database
2. **Consistent error format**: Use FastAPI's validation error response
3. **Field-level errors**: Each validation failure mapped to specific field

### Foreign Key Constraints

1. **CASCADE DELETE**: When user deleted, all tasks deleted (FR-012)
2. **RESTRICT on update**: Prevent orphaned records
3. **Index on foreign keys**: Performance for joins

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| sqlmodel | ^0.0.14 | ORM with type safety |
| pydantic | ^2.5 | Validation (via SQLModel) |
| argon2-cffi | ^23.1 | Password hashing |
| email-validator | ^2.1 | Email validation (Pydantic extra) |

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic V2 Validation](https://docs.pydantic.dev/latest/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [PostgreSQL UUID Type](https://www.postgresql.org/docs/current/datatype-uuid.html)
