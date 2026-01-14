# Implementation Plan: Data Schemas (Phase-2)

**Branch**: `005-data-schemas-phase2` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-data-schemas-phase2/spec.md`

## Summary

Implement core data schemas (User, Task) for the Todo Full-Stack Web Application Phase-2 using SQLModel ORM with PostgreSQL. The schemas provide type-safe, validated data structures with UUID primary keys, UTC timestamps, and proper relationships with cascade delete behavior.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLModel, Pydantic, argon2-cffi
**Storage**: PostgreSQL (Neon Serverless)
**Testing**: pytest (contract + integration + unit)
**Target Platform**: Linux server (containerized)
**Project Type**: Web (frontend + backend)
**Performance Goals**: Schema validations <50ms, support 10k concurrent users
**Constraints**: All timestamps UTC, password never exposed, user data isolation
**Scale/Scope**: Standard todo app, 2 entities (User, Task), 15 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-First Development | ✅ PASS | spec.md exists and approved |
| II. Layered Architecture | ✅ PASS | Models in data layer, FastAPI in application layer |
| III. Test-First Development | ✅ PASS | Contract and unit tests planned |
| IV. Secure by Design | ✅ PASS | Password hashing, user isolation, no secrets in code |
| V. API-First Integration | ✅ PASS | OpenAPI contract defined in contracts/ |
| VI. Minimal Viable Diff | ✅ PASS | Only User and Task entities, no extras |

**Re-check after Phase 1**: All gates still pass. No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/005-data-schemas-phase2/
├── plan.md              # This file
├── spec.md              # Feature requirements
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Implementation guide
├── contracts/           # Phase 1: API schemas
│   └── openapi.yaml     # OpenAPI 3.1 specification
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2: Implementation tasks (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/           # SQLModel entities
│   │   ├── __init__.py   # Model exports
│   │   ├── user.py       # User entity and schemas
│   │   └── task.py       # Task entity and schemas
│   ├── services/         # Business logic (future)
│   ├── api/              # FastAPI routes (future)
│   └── auth/             # Authentication utilities
│       └── password.py   # Argon2id hashing
└── tests/
    ├── contract/         # API schema validation tests
    │   └── test_schemas.py
    ├── integration/      # Database integration tests
    │   └── test_models_db.py
    └── unit/             # Isolated unit tests
        └── test_models.py

frontend/
├── src/
│   ├── components/       # React components (future)
│   ├── app/              # Next.js App Router (future)
│   └── services/         # API client (future)
└── tests/                # Frontend tests (future)
```

**Structure Decision**: Web application structure per Constitution §II (Layered Architecture). Backend models in `backend/src/models/`, tests split by type per Constitution §III (Test-First Development).

## Complexity Tracking

> No Constitution Check violations. No complexity justifications needed.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Phase Artifacts

### Phase 0: Research (Complete)

- [research.md](./research.md) - Technology decisions documented:
  - SQLModel for ORM
  - UUID v4 for primary keys
  - Argon2id for password hashing
  - Pydantic EmailStr for email validation
  - UTC timestamps with timezone awareness

### Phase 1: Design (Complete)

- [data-model.md](./data-model.md) - Entity definitions with:
  - User entity (id, email, password_hash, timestamps)
  - Task entity (id, user_id, title, description, is_completed, timestamps)
  - Relationship: User 1:N Task with cascade delete
  - SQLModel code examples
  - Database DDL

- [contracts/openapi.yaml](./contracts/openapi.yaml) - API contract with:
  - User schemas (UserBase, UserCreate, UserPublic)
  - Task schemas (TaskBase, TaskCreate, TaskUpdate, TaskPublic)
  - Validation error format
  - REST endpoints for CRUD operations

- [quickstart.md](./quickstart.md) - Implementation guide with:
  - Model definitions
  - Password hashing utilities
  - Usage examples
  - Validation examples

## Implementation Approach

### Key Design Decisions

1. **Separate table models from API schemas** - UserBase/TaskBase for shared fields, User/Task for database, UserPublic/TaskPublic for API responses

2. **Password handling** - UserCreate accepts plain password, converted to hash before storage, hash never exposed in UserPublic

3. **Timestamps** - Auto-generated UTC timestamps, updated_at refreshed on every modification

4. **Validation** - Dual layer: Pydantic at API boundary, database constraints as backup

5. **User isolation** - All task queries filtered by user_id, enforced at service layer

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| sqlmodel | ^0.0.14 | ORM with type safety |
| pydantic | ^2.5 | Validation (via SQLModel) |
| argon2-cffi | ^23.1 | Password hashing |
| email-validator | ^2.1 | Email validation |
| pytest | ^8.0 | Testing framework |
| pytest-asyncio | ^0.23 | Async test support |

## Next Steps

Run `/sp.tasks` to generate implementation tasks following TDD methodology:

1. RED: Write failing tests for model validation
2. GREEN: Implement models to pass tests
3. REFACTOR: Optimize if needed

## Risks

1. **Database migration complexity** - Mitigated by clean initial schema, Alembic for future migrations
2. **Password hash upgrade path** - Argon2 supports rehashing on login if parameters change
3. **Email uniqueness race conditions** - Handled by database UNIQUE constraint

---

*Generated by /sp.plan on 2026-01-13*
