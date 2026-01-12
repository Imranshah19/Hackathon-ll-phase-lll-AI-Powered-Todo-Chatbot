# Tasks: Skills Library Phase-2

**Input**: Design documents from `/specs/003-skills-library-phase2/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: REQUIRED per Constitution (Principle III: Test-First Development)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Skills**: `backend/src/services/skills/`
- **Models**: `backend/src/models/`
- **API**: `backend/src/api/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend project structure per plan.md in backend/
- [ ] T002 Initialize Python 3.11 project with FastAPI, Pydantic, SQLModel dependencies in backend/pyproject.toml
- [ ] T003 [P] Configure pytest and test structure in backend/tests/
- [ ] T004 [P] Configure linting (ruff) and formatting (black) in backend/pyproject.toml
- [ ] T005 [P] Create .env.example with required environment variables in backend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create SkillCategory enum in backend/src/models/skill.py
- [ ] T007 Create FailureCode enum in backend/src/models/failure_mode.py
- [ ] T008 Create Severity enum in backend/src/models/failure_mode.py
- [ ] T009 Create STANDARD_FAILURE_MODES mapping in backend/src/models/failure_mode.py
- [ ] T010 [P] Create SkillContext model in backend/src/services/skills/context.py
- [ ] T011 [P] Create SkillMetadata model in backend/src/services/skills/models.py
- [ ] T012 Create FailureResponse model in backend/src/models/failure_mode.py
- [ ] T013 Create generic SkillResult model in backend/src/services/skills/models.py
- [ ] T014 Create BaseSkill abstract class with Generic[TInput, TOutput] in backend/src/services/skills/base.py
- [ ] T015 Create @skill decorator for registration in backend/src/services/skills/registry.py
- [ ] T016 Create SkillRegistry class with get/register/get_for_agent methods in backend/src/services/skills/registry.py
- [ ] T017 Create skills package __init__.py with exports in backend/src/services/skills/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Skill Invocation (Priority: P1)

**Goal**: Agents can invoke skills with typed inputs and receive predictable outputs

**Independent Test**: Invoke any skill with valid inputs, verify correct output format and metadata

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] Contract test for skill input schema validation in backend/tests/contract/skills/test_skill_schemas.py
- [ ] T019 [P] [US1] Contract test for skill output schema validation in backend/tests/contract/skills/test_skill_schemas.py
- [ ] T020 [P] [US1] Contract test for SkillResult success/failure structure in backend/tests/contract/skills/test_skill_result.py
- [ ] T021 [P] [US1] Unit test for SkillExecutor.execute() in backend/tests/unit/skills/test_executor.py
- [ ] T022 [US1] Integration test for skill invocation end-to-end in backend/tests/integration/skills/test_invocation.py

### Implementation for User Story 1

- [ ] T023 [P] [US1] Create SkillExecutor class with execute() method in backend/src/services/skills/executor.py
- [ ] T024 [P] [US1] Create sample TaskCreationSkill to verify invocation pattern in backend/src/services/skills/task/task_creation.py
- [ ] T025 [US1] Create TaskCreateInput/TaskCreateOutput schemas in backend/src/services/skills/task/schemas.py
- [ ] T026 [US1] Implement SkillExecutor.execute() with duration tracking in backend/src/services/skills/executor.py
- [ ] T027 [US1] Add correlation_id generation and propagation in backend/src/services/skills/executor.py
- [ ] T028 [US1] Implement POST /skills/{skill_name}/invoke endpoint in backend/src/api/skills.py
- [ ] T029 [US1] Implement GET /skills endpoint (list all skills) in backend/src/api/skills.py
- [ ] T030 [US1] Implement GET /skills/{skill_name} endpoint (get skill definition) in backend/src/api/skills.py

**Checkpoint**: User Story 1 complete - skills can be invoked with typed inputs/outputs

---

## Phase 4: User Story 2 - Skill Composition (Priority: P1)

**Goal**: Agents can compose multiple skills together for complex operations

**Independent Test**: Chain skills A→B, verify data flows correctly; run parallel skills, verify independent completion

### Tests for User Story 2

- [ ] T031 [P] [US2] Unit test for SkillChain.then() method in backend/tests/unit/skills/test_composition.py
- [ ] T032 [P] [US2] Unit test for SkillChain.execute() with success in backend/tests/unit/skills/test_composition.py
- [ ] T033 [P] [US2] Unit test for SkillChain.execute() with mid-chain failure in backend/tests/unit/skills/test_composition.py
- [ ] T034 [P] [US2] Unit test for SkillParallel.execute() in backend/tests/unit/skills/test_composition.py
- [ ] T035 [US2] Integration test for composed skill chain in backend/tests/integration/skills/test_composition.py

### Implementation for User Story 2

- [ ] T036 [P] [US2] Create SkillChain class with then() method in backend/src/services/skills/composition.py
- [ ] T037 [US2] Implement SkillChain.execute() with fail-fast semantics in backend/src/services/skills/composition.py
- [ ] T038 [US2] Create SkillParallel class in backend/src/services/skills/composition.py
- [ ] T039 [US2] Implement SkillParallel.execute() with asyncio.gather in backend/src/services/skills/composition.py
- [ ] T040 [US2] Add output transform support to SkillChain.then() in backend/src/services/skills/composition.py
- [ ] T041 [US2] Export composition classes in backend/src/services/skills/__init__.py

**Checkpoint**: User Story 2 complete - skills can be chained and run in parallel

---

## Phase 5: User Story 3 - Skill Failure Handling (Priority: P1)

**Goal**: Skills return well-defined failure modes for consistent error handling

**Independent Test**: Trigger each failure mode, verify error response includes code, message, and recoverability

### Tests for User Story 3

- [ ] T042 [P] [US3] Unit test for FailureResponse.from_code() factory in backend/tests/unit/skills/test_failure_modes.py
- [ ] T043 [P] [US3] Unit test for wrap_unexpected_error() function in backend/tests/unit/skills/test_failure_modes.py
- [ ] T044 [P] [US3] Unit test for each FailureCode severity mapping in backend/tests/unit/skills/test_failure_modes.py
- [ ] T045 [US3] Contract test for failure response structure (no internal details exposed) in backend/tests/contract/skills/test_failure_response.py
- [ ] T046 [US3] Integration test for skill failure propagation in backend/tests/integration/skills/test_failure_handling.py

### Implementation for User Story 3

- [ ] T047 [P] [US3] Implement FailureResponse.from_code() factory method in backend/src/models/failure_mode.py
- [ ] T048 [US3] Create wrap_unexpected_error() function in backend/src/services/skills/errors.py
- [ ] T049 [US3] Add error wrapping to SkillExecutor.execute() in backend/src/services/skills/executor.py
- [ ] T050 [US3] Create SkillTimeoutError exception class in backend/src/services/skills/errors.py
- [ ] T051 [US3] Create RetryableSkillError exception class in backend/src/services/skills/errors.py
- [ ] T052 [US3] Map FailureCode to HTTP status codes in backend/src/api/skills.py
- [ ] T053 [US3] Ensure error responses sanitize internal details in backend/src/services/skills/errors.py

**Checkpoint**: User Story 3 complete - all errors return defined failure modes

---

## Phase 6: User Story 4 - Skill Validation (Priority: P1)

**Goal**: Invalid inputs are rejected early with clear validation feedback

**Independent Test**: Send malformed inputs, verify validation errors identify specific fields

### Tests for User Story 4

- [ ] T054 [P] [US4] Unit test for validate_skill_input() with valid input in backend/tests/unit/skills/test_validator.py
- [ ] T055 [P] [US4] Unit test for validate_skill_input() with missing fields in backend/tests/unit/skills/test_validator.py
- [ ] T056 [P] [US4] Unit test for validate_skill_input() with wrong types in backend/tests/unit/skills/test_validator.py
- [ ] T057 [P] [US4] Unit test for validate_skill_input() with constraint violations in backend/tests/unit/skills/test_validator.py
- [ ] T058 [US4] Contract test for validation error response format in backend/tests/contract/skills/test_validation.py

### Implementation for User Story 4

- [ ] T059 [P] [US4] Create validate_skill_input() function in backend/src/services/skills/validator.py
- [ ] T060 [US4] Implement Pydantic validation with custom field validators in backend/src/services/skills/validator.py
- [ ] T061 [US4] Format ValidationError into FailureResponse in backend/src/services/skills/validator.py
- [ ] T062 [US4] Integrate validation into SkillExecutor before execute() in backend/src/services/skills/executor.py
- [ ] T063 [US4] Add validation error details (field names, constraints) to response in backend/src/services/skills/validator.py

**Checkpoint**: User Story 4 complete - invalid inputs rejected with clear feedback

---

## Phase 7: User Story 5 - Skill Observability (Priority: P2)

**Goal**: Operators can monitor skill performance and debug issues

**Independent Test**: Execute skills, verify metrics recorded and logs produced with correlation IDs

### Tests for User Story 5

- [ ] T064 [P] [US5] Unit test for duration recording in backend/tests/unit/skills/test_observability.py
- [ ] T065 [P] [US5] Unit test for correlation_id in logs in backend/tests/unit/skills/test_observability.py
- [ ] T066 [P] [US5] Unit test for success/failure metric counters in backend/tests/unit/skills/test_observability.py
- [ ] T067 [US5] Integration test for observability across skill chain in backend/tests/integration/skills/test_observability.py

### Implementation for User Story 5

- [ ] T068 [P] [US5] Configure structlog logger in backend/src/services/skills/logging.py
- [ ] T069 [P] [US5] Define Prometheus metrics (counter, histogram) in backend/src/services/skills/metrics.py
- [ ] T070 [US5] Create ObservableSkillExecutor wrapper class in backend/src/services/skills/observable.py
- [ ] T071 [US5] Integrate logging with correlation_id binding in backend/src/services/skills/observable.py
- [ ] T072 [US5] Emit skill_invocations_total counter on execution in backend/src/services/skills/observable.py
- [ ] T073 [US5] Emit skill_duration_seconds histogram on completion in backend/src/services/skills/observable.py
- [ ] T074 [US5] Add /metrics endpoint for Prometheus scraping in backend/src/api/metrics.py

**Checkpoint**: User Story 5 complete - skills are observable

---

## Phase 8: Skill Implementation (27 Skills across 7 Categories)

**Purpose**: Implement all 27 skills defined in spec.md

### Category: Orchestration (4 skills)

- [ ] T075 [P] Create orchestration skills package in backend/src/services/skills/orchestration/__init__.py
- [ ] T076 [P] Implement request_routing skill in backend/src/services/skills/orchestration/request_routing.py
- [ ] T077 [P] Implement workflow_coordination skill in backend/src/services/skills/orchestration/workflow_coordination.py
- [ ] T078 [P] Implement response_aggregation skill in backend/src/services/skills/orchestration/response_aggregation.py
- [ ] T079 [P] Implement error_handling skill in backend/src/services/skills/orchestration/error_handling.py

### Category: Authentication (5 skills)

- [ ] T080 [P] Create auth skills package in backend/src/services/skills/auth/__init__.py
- [ ] T081 [P] Implement password_hashing skill in backend/src/services/skills/auth/password_hashing.py
- [ ] T082 [P] Implement token_generation skill in backend/src/services/skills/auth/token_generation.py
- [ ] T083 [P] Implement token_validation skill in backend/src/services/skills/auth/token_validation.py
- [ ] T084 [P] Implement rate_limiting skill in backend/src/services/skills/auth/rate_limiting.py
- [ ] T085 [P] Implement session_management skill in backend/src/services/skills/auth/session_management.py

### Category: Task Management (5 skills)

- [ ] T086 [P] Create task skills package in backend/src/services/skills/task/__init__.py
- [ ] T087 Implement task_creation skill in backend/src/services/skills/task/task_creation.py
- [ ] T088 [P] Implement task_retrieval skill in backend/src/services/skills/task/task_retrieval.py
- [ ] T089 [P] Implement task_update skill in backend/src/services/skills/task/task_update.py
- [ ] T090 [P] Implement task_deletion skill in backend/src/services/skills/task/task_deletion.py
- [ ] T091 [P] Implement ownership_validation skill in backend/src/services/skills/task/ownership_validation.py

### Category: User Management (5 skills)

- [ ] T092 [P] Create user skills package in backend/src/services/skills/user/__init__.py
- [ ] T093 [P] Implement user_creation skill in backend/src/services/skills/user/user_creation.py
- [ ] T094 [P] Implement user_retrieval skill in backend/src/services/skills/user/user_retrieval.py
- [ ] T095 [P] Implement profile_update skill in backend/src/services/skills/user/profile_update.py
- [ ] T096 [P] Implement email_validation skill in backend/src/services/skills/user/email_validation.py
- [ ] T097 [P] Implement account_deletion skill in backend/src/services/skills/user/account_deletion.py

### Category: AI (5 skills)

- [ ] T098 [P] Create AI skills package in backend/src/services/skills/ai/__init__.py
- [ ] T099 [P] Implement suggestion_generation skill with graceful degradation in backend/src/services/skills/ai/suggestion_generation.py
- [ ] T100 [P] Implement priority_analysis skill in backend/src/services/skills/ai/priority_analysis.py
- [ ] T101 [P] Implement category_inference skill in backend/src/services/skills/ai/category_inference.py
- [ ] T102 [P] Implement output_sanitization skill in backend/src/services/skills/ai/output_sanitization.py
- [ ] T103 [P] Implement graceful_degradation skill in backend/src/services/skills/ai/graceful_degradation.py

### Category: Planning (5 skills)

- [ ] T104 [P] Create planning skills package in backend/src/services/skills/planning/__init__.py
- [ ] T105 [P] Implement goal_decomposition skill in backend/src/services/skills/planning/goal_decomposition.py
- [ ] T106 [P] Implement task_sequencing skill in backend/src/services/skills/planning/task_sequencing.py
- [ ] T107 [P] Implement dependency_analysis skill in backend/src/services/skills/planning/dependency_analysis.py
- [ ] T108 [P] Implement feasibility_check skill in backend/src/services/skills/planning/feasibility_check.py
- [ ] T109 [P] Implement plan_optimization skill in backend/src/services/skills/planning/plan_optimization.py

### Category: Execution (5 skills)

- [ ] T110 [P] Create execution skills package in backend/src/services/skills/execution/__init__.py
- [ ] T111 [P] Implement task_execution skill in backend/src/services/skills/execution/task_execution.py
- [ ] T112 [P] Implement progress_reporting skill in backend/src/services/skills/execution/progress_reporting.py
- [ ] T113 [P] Implement failure_handling skill in backend/src/services/skills/execution/failure_handling.py
- [ ] T114 [P] Implement retry_logic skill in backend/src/services/skills/execution/retry_logic.py
- [ ] T115 [P] Implement state_management skill in backend/src/services/skills/execution/state_management.py

**Checkpoint**: All 27 skills implemented

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cross-cutting improvements

- [ ] T116 [P] Add unit tests for all 27 skills in backend/tests/unit/skills/
- [ ] T117 [P] Add contract tests for all skill schemas in backend/tests/contract/skills/
- [ ] T118 Run quickstart.md validation scenarios
- [ ] T119 Implement GET /skills/categories endpoint in backend/src/api/skills.py
- [ ] T120 Implement GET /skills/failure-modes endpoint in backend/src/api/skills.py
- [ ] T121 Add OpenAPI documentation annotations in backend/src/api/skills.py
- [ ] T122 Security review: verify FR-018 (no internal details exposed) across all skills
- [ ] T123 Performance validation: verify p95 <200ms for non-AI skills

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 (Invocation): No dependencies on other stories
  - US2 (Composition): No dependencies on other stories
  - US3 (Failure Handling): No dependencies on other stories
  - US4 (Validation): No dependencies on other stories
  - US5 (Observability): No dependencies on other stories
- **Skill Implementation (Phase 8)**: Depends on US1-US4 completion
- **Polish (Phase 9)**: Depends on all phases complete

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Invocation) | Foundational | Phase 2 |
| US2 (Composition) | Foundational | Phase 2 |
| US3 (Failure) | Foundational | Phase 2 |
| US4 (Validation) | Foundational | Phase 2 |
| US5 (Observability) | Foundational | Phase 2 |

### Parallel Opportunities

**Within Setup (Phase 1):**
```
T003, T004, T005 can run in parallel
```

**Within Foundational (Phase 2):**
```
T010, T011 can run in parallel (after T006-T009)
```

**User Stories can run in parallel after Foundational:**
```
Phase 3 (US1) || Phase 4 (US2) || Phase 5 (US3) || Phase 6 (US4) || Phase 7 (US5)
```

**Within Skill Implementation (Phase 8):**
```
All category packages can be created in parallel
All skills within a category can be implemented in parallel
```

---

## Parallel Example: User Story 1

```bash
# Launch all tests in parallel:
Task: "Contract test for skill input schema validation"
Task: "Contract test for skill output schema validation"
Task: "Contract test for SkillResult success/failure structure"
Task: "Unit test for SkillExecutor.execute()"

# Launch parallel implementation tasks:
Task: "Create SkillExecutor class"
Task: "Create sample TaskCreationSkill"
```

---

## Implementation Strategy

### MVP First (User Stories 1-4)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Skill Invocation)
4. **VALIDATE**: Test skill invocation works
5. Complete Phases 4-6: User Stories 2-4 (Composition, Failure, Validation)
6. **VALIDATE**: Core skills library functional

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (Invocation) → Can invoke skills
3. US4 (Validation) → Inputs validated
4. US3 (Failure) → Errors handled consistently
5. US2 (Composition) → Skills can be chained
6. US5 (Observability) → Monitoring enabled
7. Phase 8 → All 27 skills implemented
8. Phase 9 → Polish and validation

### Suggested MVP Scope

**MVP = Phases 1-6 (US1-US4)**
- Skill invocation works
- Input validation works
- Failure handling works
- Composition works
- Sample skills demonstrate patterns

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 123 |
| Setup Tasks | 5 |
| Foundational Tasks | 12 |
| US1 (Invocation) Tasks | 13 |
| US2 (Composition) Tasks | 11 |
| US3 (Failure Handling) Tasks | 12 |
| US4 (Validation) Tasks | 10 |
| US5 (Observability) Tasks | 11 |
| Skill Implementation Tasks | 41 |
| Polish Tasks | 8 |
| Parallel Opportunities | 80+ tasks |
| Independent Test Criteria | 5 (one per story) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Tests MUST be written and FAIL before implementation (TDD per Constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
