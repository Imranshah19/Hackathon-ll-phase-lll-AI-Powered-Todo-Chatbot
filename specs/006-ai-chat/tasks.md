# Tasks: Phase 3 AI Chat

**Input**: Design documents from `/specs/006-ai-chat/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/chat-api.yaml

**Tests**: Tests are included per Constitution Principle III (Test-First Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths follow plan.md project structure

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and AI integration dependencies

- [x] T001 Add OpenAI and Anthropic SDK dependencies to backend/pyproject.toml
- [x] T002 [P] Create backend/src/ai/__init__.py module initialization
- [x] T003 [P] Create AI configuration in backend/src/config/ai_config.py with API keys from .env
- [x] T004 [P] Create InterpretedCommand dataclass in backend/src/ai/types.py
- [x] T005 Add OPENAI_API_KEY and ANTHROPIC_API_KEY to .env.example

**Status**: ALL COMPLETE - Ready for Phase 2

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**STATUS**: ✅ ALL FOUNDATIONAL TASKS COMPLETE - User stories can proceed

### Database Models

- [x] T006 Create Conversation model in backend/src/models/conversation.py per data-model.md
- [x] T007 [P] Create Message model in backend/src/models/message.py per data-model.md
- [x] T008 Create Alembic migration for conversations and messages tables in backend/alembic/versions/

### AI Core Components

- [x] T009 Create intent extraction prompts in backend/src/ai/prompts/intent.py with function calling schema
- [x] T010 [P] Create response generation prompts in backend/src/ai/prompts/response.py
- [x] T011 Implement AI interpreter in backend/src/ai/interpreter.py with OpenAI function calling
- [x] T012 Implement Bonsai CLI executor bridge in backend/src/ai/executor.py calling existing task_service
- [x] T013 Implement confidence-based fallback logic in backend/src/ai/fallback.py (tiers: >0.8, 0.5-0.8, <0.5)

### Chat Service Layer

- [x] T014 Create ChatService in backend/src/services/chat_service.py orchestrating interpreter → executor → response
- [x] T015 [P] Create ConversationService in backend/src/services/conversation_service.py for CRUD operations

### API Endpoints (Foundation)

- [x] T016 Create chat API router in backend/src/api/chat.py with POST /chat/message endpoint
- [x] T017 [P] Create conversations API router in backend/src/api/conversations.py with CRUD endpoints
- [x] T018 Register chat and conversations routers in backend/src/main.py

### Frontend Foundation

- [x] T019 Create chat API client in frontend/src/lib/api.ts with sendMessage and conversation methods
- [x] T020 [P] Create ChatWindow component shell in frontend/src/components/chat/ChatWindow.tsx
- [x] T021 [P] Create MessageBubble component in frontend/src/components/chat/MessageBubble.tsx
- [x] T022 [P] Create InputBar component in frontend/src/components/chat/InputBar.tsx
- [x] T023 Create chat page in frontend/src/app/chat/page.tsx integrating ChatWindow

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) ✅ COMPLETE

**Goal**: Users can create tasks via natural language like "Add a task to buy groceries tomorrow"

**Independent Test**: Send NL message to create task, verify task appears with correct title and due date

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T024 [P] [US1] Contract test for POST /chat/message create action in backend/tests/contract/test_chat_create.py
- [x] T025 [P] [US1] Unit test for add intent extraction in backend/tests/unit/test_interpreter_add.py
- [x] T026 [P] [US1] Integration test for create task via chat in backend/tests/integration/test_chat_create_flow.py

### Implementation for User Story 1

- [x] T027 [US1] Implement "add" action intent extraction in backend/src/ai/interpreter.py
- [x] T028 [US1] Implement "add" action execution in backend/src/ai/executor.py calling task_service.create_task
- [x] T029 [US1] Add task creation response formatting in backend/src/ai/prompts/response.py
- [x] T030 [US1] Handle ambiguous "add" commands with clarification request in ChatService
- [x] T031 [US1] Add frontend display for task creation confirmation in MessageBubble.tsx

**Checkpoint**: ✅ User Story 1 complete - users can create tasks via natural language

---

## Phase 4: User Story 2 - Natural Language Task Listing (Priority: P2) ✅ COMPLETE

**Goal**: Users can view tasks by asking "What are my pending tasks?" or "What's due today?"

**Independent Test**: Send NL query, verify correct tasks returned matching criteria

**STATUS**: ✅ Tests and implementation complete. Ready to push.

### Tests for User Story 2

- [x] T032 [P] [US2] Contract test for POST /chat/message list action in backend/tests/contract/test_chat_list.py
- [x] T033 [P] [US2] Unit test for list intent extraction in backend/tests/unit/test_interpreter_list.py
- [x] T034 [P] [US2] Integration test for list tasks via chat in backend/tests/integration/test_chat_list_flow.py

### Implementation for User Story 2

- [x] T035 [US2] Implement "list" action intent extraction with status_filter in backend/src/ai/interpreter.py
- [x] T036 [US2] Implement "list" action execution in backend/src/ai/executor.py calling task_service.list_tasks
- [x] T037 [US2] Add task list response formatting in backend/src/ai/prompts/response.py
- [x] T038 [US2] Handle "no tasks" friendly message in ChatService (build_list_response handles empty lists)
- [x] T039 [US2] Add frontend display for task list in MessageBubble.tsx with TaskSummary rendering

**Checkpoint**: User Stories 1 AND 2 complete - users can create and view tasks via NL

---

## Phase 5: User Story 3 - Natural Language Task Completion (Priority: P3) ✅ COMPLETE

**Goal**: Users can mark tasks complete via "Mark task 3 as done" or "I finished buying groceries"

**Independent Test**: Create task, complete via NL, verify status changes to completed

**STATUS**: ✅ Tests and implementation complete. Ready to push.

### Tests for User Story 3

- [x] T040 [P] [US3] Contract test for POST /chat/message complete action in backend/tests/contract/test_chat_complete.py
- [x] T041 [P] [US3] Unit test for complete intent extraction in backend/tests/unit/test_interpreter_complete.py
- [x] T042 [P] [US3] Integration test for complete task via chat in backend/tests/integration/test_chat_complete_flow.py

### Implementation for User Story 3

- [x] T043 [US3] Implement "complete" action intent extraction (by ID and by title match) in backend/src/ai/interpreter.py
- [x] T044 [US3] Implement "complete" action execution in backend/src/ai/executor.py calling task_service.complete_task
- [x] T045 [US3] Add task completion response formatting in backend/src/ai/prompts/response.py
- [x] T046 [US3] Handle non-existent task error in ChatService with helpful message
- [x] T047 [US3] Handle multiple task matches by prompting user to specify ID

**Checkpoint**: User Stories 1-3 complete - core create/view/complete workflow functional

---

## Phase 6: User Story 4 - Natural Language Task Updates (Priority: P4) ✅ COMPLETE

**Goal**: Users can update tasks via "Change task 1 title to 'Call mom tonight'"

**Independent Test**: Create task, update via NL, verify changes persist

**STATUS**: ✅ Tests and implementation complete. Ready to push.

### Tests for User Story 4

- [x] T048 [P] [US4] Contract test for POST /chat/message update action in backend/tests/contract/test_chat_update.py
- [x] T049 [P] [US4] Unit test for update intent extraction in backend/tests/unit/test_interpreter_update.py
- [x] T050 [P] [US4] Integration test for update task via chat in backend/tests/integration/test_chat_update_flow.py

### Implementation for User Story 4

- [x] T051 [US4] Implement "update" action intent extraction (title, due_date) in backend/src/ai/interpreter.py
- [x] T052 [US4] Implement "update" action execution in backend/src/ai/executor.py calling task_service.update_task
- [x] T053 [US4] Add task update response formatting in backend/src/ai/prompts/response.py
- [x] T054 [US4] Handle incomplete update (missing field) with clarification prompt

**Checkpoint**: User Stories 1-4 complete - full CRUD minus delete

---

## Phase 7: User Story 5 - Natural Language Task Deletion (Priority: P5) ✅ COMPLETE

**Goal**: Users can delete tasks via "Delete task 2" or "Remove the grocery task"

**Independent Test**: Create task, delete via NL, verify no longer in list

**STATUS**: ✅ Tests and implementation complete. Ready to push.

### Tests for User Story 5

- [x] T055 [P] [US5] Contract test for POST /chat/message delete action in backend/tests/contract/test_chat_delete.py
- [x] T056 [P] [US5] Unit test for delete intent extraction in backend/tests/unit/test_interpreter_delete.py
- [x] T057 [P] [US5] Integration test for delete task via chat in backend/tests/integration/test_chat_delete_flow.py

### Implementation for User Story 5

- [x] T058 [US5] Implement "delete" action intent extraction in backend/src/ai/interpreter.py
- [x] T059 [US5] Implement "delete" action execution in backend/src/ai/executor.py calling task_service.delete_task
- [x] T060 [US5] Add deletion confirmation prompt before executing destructive action (via fallback_handler.should_confirm)
- [x] T061 [US5] Add task deletion response formatting in backend/src/ai/prompts/response.py

**Checkpoint**: User Stories 1-5 complete - full CRUD via natural language

---

## Phase 8: User Story 6 - Graceful Fallback to CLI (Priority: P6) ✅ COMPLETE

**Goal**: When AI fails or confidence is low, provide CLI command alternatives

**Independent Test**: Simulate AI failure, verify CLI instructions returned

**STATUS**: ✅ Tests and implementation complete. Ready to push.

### Tests for User Story 6

- [x] T062 [P] [US6] Contract test for 503 fallback response in backend/tests/contract/test_chat_fallback.py
- [x] T063 [P] [US6] Unit test for confidence-based fallback in backend/tests/unit/test_fallback.py
- [x] T064 [P] [US6] Integration test for AI timeout fallback in backend/tests/integration/test_chat_timeout.py

### Implementation for User Story 6

- [x] T065 [US6] Implement 5-second AI timeout with asyncio.wait_for in backend/src/ai/interpreter.py
- [x] T066 [US6] Implement low-confidence fallback with CLI suggestion in ChatService
- [x] T067 [US6] Implement AI unavailable handler returning FallbackResponse
- [x] T068 [US6] Create FallbackCLI component in frontend/src/components/chat/FallbackCLI.tsx
- [x] T069 [US6] Add "/cli" command detection to bypass AI in ChatService (_is_cli_command method)
- [x] T070 [US6] Add fallback UI rendering in ChatWindow when FallbackResponse received

**Checkpoint**: All 6 user stories complete - feature fully functional with graceful degradation

---

## Phase 9: Polish & Cross-Cutting Concerns ✅ COMPLETE

**Purpose**: Improvements that affect multiple user stories

**STATUS**: ✅ ALL TASKS COMPLETE (documentation tasks skipped per CLAUDE.md)

### Conversation Management

- [x] T071 [P] Add conversation list UI in frontend/src/app/chat/page.tsx sidebar
- [x] T072 [P] Add conversation history loading on page mount
- [x] T073 Add conversation title auto-generation from first message (auto_title_conversation in ChatService)

### Edge Cases & Validation

- [x] T074 Add empty message handling with help examples in ChatService (min_length=1 validation + frontend trim check)
- [x] T075 [P] Add message length validation (max 2000 chars) with warning (backend max_length + frontend maxLength with counter)
- [x] T076 Add direct CLI command detection (starts with "bonsai") to bypass AI (_is_cli_command method)

### Logging & Debugging

- [x] T077 Add AI interpretation logging with confidence scores in backend/src/ai/interpreter.py (logger.info in chat_service.py)
- [x] T078 [P] Add request/response logging middleware for chat endpoints (ChatLoggingMiddleware in src/middleware/logging.py)

### Documentation

- [ ] T079 Update quickstart.md with actual test commands after implementation (skipped - documentation)
- [ ] T080 Add example conversation screenshots to documentation (skipped - documentation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-8 (User Stories)**: All depend on Phase 2 completion
  - US1 (P1): Can start immediately after Phase 2
  - US2 (P2): Can start in parallel with US1 (independent)
  - US3 (P3): Can start in parallel (independent)
  - US4 (P4): Can start in parallel (independent)
  - US5 (P5): Can start in parallel (independent)
  - US6 (P6): Can start in parallel (independent)
- **Phase 9 (Polish)**: Depends on all user stories

### User Story Independence

All user stories (US1-US6) are independently testable:
- US1: Create task only
- US2: List tasks only (uses existing Phase 2 tasks)
- US3: Complete task (creates then completes)
- US4: Update task (creates then updates)
- US5: Delete task (creates then deletes)
- US6: Fallback (any input with AI failure simulation)

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Intent extraction before execution
3. Execution before response formatting
4. Backend before frontend display
5. Core flow before edge cases

### Parallel Opportunities

**Phase 1 (all parallel)**:
```
T002, T003, T004, T005
```

**Phase 2 (grouped parallels)**:
```
Models: T006, T007 (parallel)
Prompts: T009, T010 (parallel)
Services: T014, T015 (parallel)
Routers: T016, T017 (parallel)
Frontend: T019, T020, T021, T022 (parallel)
```

**Each User Story Phase**:
```
Tests: T024, T025, T026 (all parallel within story)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (NL Task Creation)
4. **STOP and VALIDATE**: Test independently
5. Demo: "Add a task to buy groceries tomorrow"

### Incremental Delivery

| Increment | Stories | Demo Capability |
|-----------|---------|-----------------|
| MVP | US1 | Create tasks via NL |
| v0.2 | US1 + US2 | Create + List |
| v0.3 | US1-US3 | Create + List + Complete |
| v0.4 | US1-US4 | Full CRUD minus Delete |
| v0.5 | US1-US5 | Full CRUD |
| v1.0 | US1-US6 | Full feature with fallback |

### Task Count Summary

| Phase | Tasks | Parallel |
|-------|-------|----------|
| Setup | 5 | 4 |
| Foundational | 18 | 10 |
| US1 (P1) | 8 | 3 |
| US2 (P2) | 8 | 3 |
| US3 (P3) | 8 | 3 |
| US4 (P4) | 7 | 3 |
| US5 (P5) | 7 | 3 |
| US6 (P6) | 9 | 3 |
| Polish | 10 | 4 |
| **Total** | **80** | **36** |

---

## Notes

- All tasks follow TDD: Tests written first, must fail before implementation
- [P] tasks can run in parallel (different files, no dependencies)
- [Story] labels map tasks to user stories for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently

---

## When to Stop and Push

### Push Policy (Constitution Principle III - Test-First)

**RULE**: Never push code without passing tests for that feature increment.

### Current State Summary

| Phase | Status | Tests | Implementation | Ready to Push? |
|-------|--------|-------|----------------|----------------|
| Phase 1: Setup | ✅ COMPLETE | N/A | ✅ Done | ✅ YES (already pushed) |
| Phase 2: Foundational | ✅ COMPLETE | N/A | ✅ Done | ✅ YES (already pushed) |
| US1: Create | ✅ COMPLETE | ✅ Done | ✅ Done | ✅ YES (already pushed) |
| US2: List | ✅ COMPLETE | ✅ Done | ✅ Done | ✅ YES (pushed) |
| US3: Complete | ✅ COMPLETE | ✅ Done | ✅ Done | ✅ YES (pushed) |
| US4: Update | ✅ COMPLETE | ✅ Done | ✅ Done | ✅ YES (pushed) |
| US5: Delete | ✅ COMPLETE | ✅ Done | ✅ Done | ✅ YES (pushed) |
| US6: Fallback | ✅ COMPLETE | ✅ Done | ✅ Done | ✅ YES (pushed) |
| Phase 9: Polish | ✅ COMPLETE | N/A | ✅ Done | ✅ YES - Ready to push |

### Valid Stop Points (Checkpoints)

Each checkpoint is independently deployable and testable:

1. **✅ MVP (Current)**: Phase 1 + Phase 2 + US1
   - Status: PUSHED
   - Demo: "Add a task to buy groceries tomorrow"

2. **⏳ v0.2**: MVP + US2 (List)
   - Requires: T032-T034 tests passing
   - Demo: "What are my pending tasks?"

3. **⏳ v0.3**: v0.2 + US3 (Complete)
   - Requires: T040-T042 tests passing
   - Demo: "Mark task 1 as done"

4. **⏳ v0.4**: v0.3 + US4 (Update)
   - Requires: T048-T050 tests passing
   - Demo: "Update task 1 title to 'Call mom tonight'"

5. **⏳ v0.5**: v0.4 + US5 (Delete)
   - Requires: T055-T057 tests passing
   - Demo: "Delete task 2"

6. **⏳ v1.0**: v0.5 + US6 (Fallback) + Polish
   - Requires: All tests passing
   - Demo: Full feature with graceful degradation

### Immediate Next Steps

To reach the next valid push point (v0.2), complete these tasks in order:

1. **Write US2 Tests** (T032-T034):
   ```
   backend/tests/contract/test_chat_list.py
   backend/tests/unit/test_interpreter_list.py
   backend/tests/integration/test_chat_list_flow.py
   ```

2. **Run tests** - ensure they pass with existing implementation

3. **Fix any failing tests** - adjust implementation if needed

4. **Commit and push** with message: `feat(chat): Add natural language task listing (US2)`

### Test Commands

```bash
# Run all Phase 3 tests
cd backend && pytest tests/ -k "chat or interpreter or fallback" -v

# Run specific user story tests
pytest tests/ -k "test_chat_list" -v      # US2
pytest tests/ -k "test_chat_complete" -v  # US3
pytest tests/ -k "test_chat_update" -v    # US4
pytest tests/ -k "test_chat_delete" -v    # US5
pytest tests/ -k "test_fallback" -v       # US6
```

### Continuous Implementation Flow

```
For each User Story (US2-US6):
  1. Write tests (Red) → Tests should FAIL
  2. Verify implementation makes tests pass (Green)
  3. Refactor if needed
  4. Run full test suite
  5. Commit with: feat(chat): <user story description>
  6. Push to remote
  7. Move to next User Story
```
