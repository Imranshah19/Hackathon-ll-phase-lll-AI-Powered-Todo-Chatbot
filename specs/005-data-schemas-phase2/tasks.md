# Tasks: Data Schemas (Phase-2)

**Input**: Design documents from `/specs/005-data-schemas-phase2/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: REQUIRED per Constitution §III (Test-First Development is NON-NEGOTIABLE)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Models: `backend/src/models/`
- Auth utilities: `backend/src/auth/`
- Tests: `backend/tests/{contract,integration,unit}/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md: `backend/src/{models,services,api,auth}`, `backend/tests/{contract,integration,unit}`
- [x] T002 Initialize Python project with pyproject.toml including dependencies: sqlmodel, pydantic, argon2-cffi, email-validator, pytest, pytest-asyncio
- [x] T003 [P] Create backend/src/__init__.py with package initialization
- [x] T004 [P] Create backend/src/models/__init__.py for model exports
- [x] T005 [P] Create backend/src/auth/__init__.py for auth utilities
- [x] T006 [P] Configure pytest in pyproject.toml with test paths and markers

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create utc_now() helper function in backend/src/models/base.py for UTC timestamp generation
- [x] T008 [P] Create base SQLModel configuration in backend/src/models/base.py with common imports
- [x] T009 [P] Create conftest.py in backend/tests/conftest.py with pytest fixtures for testing
- [x] T010 Create database session utilities in backend/src/db.py (engine, get_session)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Account Data Structure (Priority: P1) 🎯 MVP

**Goal**: Implement User entity with email validation, password hashing, and secure API schemas

**Independent Test**: Create user records, validate email format, verify password is hashed, confirm password_hash never exposed

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US1] Unit test for User model creation in backend/tests/unit/test_user_model.py - test UUID generation, timestamps
- [x] T012 [P] [US1] Unit test for UserCreate validation in backend/tests/unit/test_user_model.py - test email format, password min length
- [x] T013 [P] [US1] Unit test for UserPublic schema in backend/tests/unit/test_user_model.py - verify password_hash excluded
- [x] T014 [P] [US1] Unit test for password hashing in backend/tests/unit/test_password.py - test hash and verify functions
- [x] T015 [P] [US1] Contract test for user schemas in backend/tests/contract/test_user_schemas.py - validate against OpenAPI spec

### Implementation for User Story 1

- [x] T016 [P] [US1] Implement password hashing utilities (hash_password, verify_password) in backend/src/auth/password.py using argon2-cffi
- [x] T017 [US1] Create UserBase model with email: EmailStr in backend/src/models/user.py
- [x] T018 [US1] Create User table model with id, password_hash, timestamps in backend/src/models/user.py
- [x] T019 [US1] Create UserCreate schema with password field (min 8 chars) in backend/src/models/user.py
- [x] T020 [US1] Create UserPublic schema excluding password_hash in backend/src/models/user.py
- [x] T021 [US1] Export User models from backend/src/models/__init__.py
- [x] T022 [US1] Run User Story 1 tests and verify all pass

**Checkpoint**: User entity complete - can create users with validated email, hashed password, secure API responses

---

## Phase 4: User Story 2 - Task Data Structure (Priority: P1)

**Goal**: Implement Task entity with user relationship, title/description validation, and cascade delete

**Independent Test**: Create tasks for user, validate field constraints, verify user_id relationship, test cascade delete

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T023 [P] [US2] Unit test for Task model creation in backend/tests/unit/test_task_model.py - test UUID, defaults, timestamps
- [x] T024 [P] [US2] Unit test for TaskCreate validation in backend/tests/unit/test_task_model.py - test title length, description max
- [x] T025 [P] [US2] Unit test for TaskUpdate schema in backend/tests/unit/test_task_model.py - test partial updates
- [x] T026 [P] [US2] Unit test for TaskPublic schema in backend/tests/unit/test_task_model.py - verify all fields included
- [x] T027 [P] [US2] Contract test for task schemas in backend/tests/contract/test_task_schemas.py - validate against OpenAPI spec
- [x] T028 [US2] Integration test for User-Task relationship in backend/tests/integration/test_user_task_relationship.py - cascade delete

### Implementation for User Story 2

- [x] T029 [US2] Create TaskBase model with title, description, is_completed in backend/src/models/task.py
- [x] T030 [US2] Create Task table model with id, user_id FK, timestamps in backend/src/models/task.py
- [x] T031 [US2] Add Relationship to User model for tasks list in backend/src/models/user.py
- [x] T032 [US2] Add Relationship to Task model for user back-reference in backend/src/models/task.py
- [x] T033 [US2] Create TaskCreate schema in backend/src/models/task.py
- [x] T034 [US2] Create TaskUpdate schema with optional fields in backend/src/models/task.py
- [x] T035 [US2] Create TaskPublic schema in backend/src/models/task.py
- [x] T036 [US2] Export Task models from backend/src/models/__init__.py
- [x] T037 [US2] Run User Story 2 tests and verify all pass

**Checkpoint**: Task entity complete - can create/update tasks with validation, proper user relationship, cascade delete works

---

## Phase 5: User Story 3 - Data Validation Rules (Priority: P1)

**Goal**: Ensure consistent validation across all schemas with field-level error messages

**Independent Test**: Submit invalid data, verify specific field errors returned in consistent format

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T038 [P] [US3] Unit test for email validation errors in backend/tests/unit/test_validation_errors.py
- [x] T039 [P] [US3] Unit test for password validation errors in backend/tests/unit/test_validation_errors.py
- [x] T040 [P] [US3] Unit test for title validation errors in backend/tests/unit/test_validation_errors.py
- [x] T041 [P] [US3] Unit test for description validation errors in backend/tests/unit/test_validation_errors.py
- [x] T042 [P] [US3] Contract test for ValidationError schema in backend/tests/contract/test_validation_contract.py

### Implementation for User Story 3

- [x] T043 [US3] Add custom error messages to UserCreate email field in backend/src/models/user.py
- [x] T044 [US3] Add custom error messages to UserCreate password field in backend/src/models/user.py
- [x] T045 [US3] Add custom error messages to TaskBase title field in backend/src/models/task.py
- [x] T046 [US3] Add custom error messages to TaskBase description field in backend/src/models/task.py
- [x] T047 [US3] Run User Story 3 tests and verify all pass

**Checkpoint**: Validation complete - all invalid data rejected with specific, actionable field-level errors

---

## Phase 6: User Story 4 - Schema Evolution Support (Priority: P2)

**Goal**: Ensure schemas support forward compatibility with optional fields and defaults

**Independent Test**: Add optional field, verify existing data remains valid, test default value handling

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T048 [P] [US4] Unit test for optional field handling in backend/tests/unit/test_schema_evolution.py - nullable fields
- [x] T049 [P] [US4] Unit test for default values in backend/tests/unit/test_schema_evolution.py - is_completed default
- [x] T050 [P] [US4] Unit test for partial updates in backend/tests/unit/test_schema_evolution.py - TaskUpdate with missing fields

### Implementation for User Story 4

- [x] T051 [US4] Document schema evolution patterns in backend/src/models/README.md
- [x] T052 [US4] Verify all optional fields have proper defaults in backend/src/models/task.py
- [x] T053 [US4] Verify TaskUpdate handles missing fields gracefully in backend/src/models/task.py
- [x] T054 [US4] Run User Story 4 tests and verify all pass

**Checkpoint**: Schema evolution ready - new optional fields can be added without breaking existing data

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [x] T055 [P] Run full test suite: `pytest backend/tests/ -v`
- [x] T056 [P] Validate all models against quickstart.md examples in backend/tests/integration/test_quickstart_examples.py
- [x] T057 [P] Generate test coverage report: `pytest backend/tests/ --cov=backend/src`
- [x] T058 Update backend/src/models/__init__.py with complete exports
- [x] T059 Verify all 15 functional requirements (FR-001 to FR-015) are implemented
- [x] T060 Run final validation against data-model.md traceability table

**Checkpoint**: Feature complete - all 60 tasks completed, 163 tests passing, 96% coverage on models/auth

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 and US2: Can proceed in parallel (P1 priority, different entities)
  - US3: Depends on US1 and US2 (validates their schemas)
  - US4: Can proceed after US2 (tests schema patterns)
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - Requires User model from US1 for relationship
- **User Story 3 (P1)**: Depends on US1 and US2 - Tests validation on their schemas
- **User Story 4 (P2)**: Can start after US2 - Tests evolution patterns

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before schemas
- Base models before table models
- Table models before API schemas
- Run story tests after implementation

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005, T006 can run in parallel

**Phase 2 (Foundational)**:
- T008, T009 can run in parallel

**User Story 1 Tests**:
- T011, T012, T013, T014, T015 can run in parallel

**User Story 2 Tests**:
- T023, T024, T025, T026, T027 can run in parallel

**User Story 3 Tests**:
- T038, T039, T040, T041, T042 can run in parallel

**User Story 4 Tests**:
- T048, T049, T050 can run in parallel

**Phase 7 (Polish)**:
- T055, T056, T057 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "T011 Unit test for User model creation in backend/tests/unit/test_user_model.py"
Task: "T012 Unit test for UserCreate validation in backend/tests/unit/test_user_model.py"
Task: "T013 Unit test for UserPublic schema in backend/tests/unit/test_user_model.py"
Task: "T014 Unit test for password hashing in backend/tests/unit/test_password.py"
Task: "T015 Contract test for user schemas in backend/tests/contract/test_user_schemas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User model independently
5. Deploy/demo if ready - User registration foundation complete

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → User model MVP
3. Add User Story 2 → Test independently → Task model with relationships
4. Add User Story 3 → Test independently → Full validation
5. Add User Story 4 → Test independently → Evolution patterns
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (User model)
   - Developer B: User Story 2 (Task model) - can start after T018 creates User model
3. After US1 + US2:
   - Developer A: User Story 3 (Validation)
   - Developer B: User Story 4 (Evolution)
4. Stories complete and integrate independently

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 60 |
| **Phase 1 (Setup)** | 6 |
| **Phase 2 (Foundational)** | 4 |
| **User Story 1** | 12 (5 tests + 7 impl) |
| **User Story 2** | 15 (6 tests + 9 impl) |
| **User Story 3** | 10 (5 tests + 5 impl) |
| **User Story 4** | 7 (3 tests + 4 impl) |
| **Phase 7 (Polish)** | 6 |
| **Parallel Opportunities** | 28 tasks marked [P] |

**Suggested MVP Scope**: Complete through User Story 1 (22 tasks) for minimal User model functionality.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable
- Verify tests fail before implementing (TDD per Constitution §III)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently

---

*Generated by /sp.tasks on 2026-01-13*
