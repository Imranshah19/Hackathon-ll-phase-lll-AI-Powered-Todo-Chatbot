# Task Dependency Graph — Phase 2

**Project**: Todo Full-Stack Web Application
**Phase**: 2 — System Design & Architecture
**Created**: 2026-01-14
**Status**: Active

---

## 1. Feature Dependency Graph

```
                    ┌─────────────────────────┐
                    │   001-specify-setup     │
                    │   (Project Foundation)  │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  004-task-graph-phase2  │
                    │  (Dependency Planning)  │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  005-data-schemas-phase2│◄─────── COMPLETE
                    │  (User, Task, Auth)     │         163 tests
                    └───────────┬─────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│ 006-auth-endpoints  │ │ 007-task-endpoints  │ │ 008-user-endpoints  │
│ (Login, Register)   │ │ (CRUD API)          │ │ (Profile API)       │
└─────────┬───────────┘ └─────────┬───────────┘ └─────────┬───────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  009-api-integration    │
                    │  (E2E API Tests)        │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  010-ai-features        │
                    │  (Optional AI Agent)    │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  011-frontend-scaffold  │
                    │  (Next.js Setup)        │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  012-frontend-auth      │
                    │  (Login/Register UI)    │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  013-frontend-tasks     │
                    │  (Task Management UI)   │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  014-e2e-testing        │
                    │  (Full System Tests)    │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  015-deployment         │
                    │  (Production Ready)     │
                    └─────────────────────────┘
```

---

## 2. Feature Details

### Completed Features

| ID | Feature | Status | Tests | Coverage |
|----|---------|--------|-------|----------|
| 001 | specify-setup | Complete | — | — |
| 004 | task-graph-phase2 | Complete | — | — |
| 005 | data-schemas-phase2 | **Complete** | 163 | 96% |

### Pending Features

| ID | Feature | Dependencies | Priority | Estimate |
|----|---------|--------------|----------|----------|
| 006 | auth-endpoints | 005 | P0 | — |
| 007 | task-endpoints | 005 | P0 | — |
| 008 | user-endpoints | 005 | P1 | — |
| 009 | api-integration | 006, 007, 008 | P0 | — |
| 010 | ai-features | 009 | P2 | — |
| 011 | frontend-scaffold | — | P1 | — |
| 012 | frontend-auth | 006, 011 | P0 | — |
| 013 | frontend-tasks | 007, 012 | P0 | — |
| 014 | e2e-testing | 012, 013 | P0 | — |
| 015 | deployment | 014 | P0 | — |

---

## 3. Critical Path

The critical path for Phase 2 completion:

```
005 → 006 → 007 → 009 → 011 → 012 → 013 → 014 → 015
                                                  ↑
                                           MVP COMPLETE
```

### Parallel Tracks

| Track | Features | Can Start |
|-------|----------|-----------|
| Backend API | 006, 007, 008 | After 005 |
| Frontend | 011 | Immediately |
| AI (Optional) | 010 | After 009 |

---

## 4. Component Dependencies

### Backend Dependencies

```
backend/src/
├── models/          ◄── 005 (COMPLETE)
│   ├── user.py
│   ├── task.py
│   └── base.py
├── auth/            ◄── 005 (PARTIAL)
│   └── password.py
├── api/             ◄── 006, 007, 008
│   ├── auth.py
│   ├── tasks.py
│   └── users.py
├── services/        ◄── 006, 007, 008
│   ├── auth.py
│   ├── task.py
│   └── user.py
└── agents/          ◄── 009, 010
    ├── orchestrator.py
    ├── auth.py
    ├── task.py
    ├── user.py
    └── ai.py
```

### Frontend Dependencies

```
frontend/src/
├── app/             ◄── 011
│   ├── layout.tsx
│   ├── page.tsx
│   ├── login/       ◄── 012
│   ├── register/    ◄── 012
│   └── tasks/       ◄── 013
├── components/      ◄── 011
│   ├── auth/        ◄── 012
│   └── tasks/       ◄── 013
└── services/        ◄── 012
    └── api.ts
```

---

## 5. Test Dependencies

```
tests/
├── unit/                    ◄── Per-feature
│   ├── test_user_model.py   ◄── 005 ✓
│   ├── test_task_model.py   ◄── 005 ✓
│   ├── test_password.py     ◄── 005 ✓
│   ├── test_auth_service.py ◄── 006
│   ├── test_task_service.py ◄── 007
│   └── test_user_service.py ◄── 008
├── contract/                ◄── Per-feature
│   ├── test_user_schemas.py ◄── 005 ✓
│   ├── test_task_schemas.py ◄── 005 ✓
│   ├── test_auth_api.py     ◄── 006
│   └── test_task_api.py     ◄── 007
├── integration/             ◄── Cross-feature
│   ├── test_user_task.py    ◄── 005 ✓
│   ├── test_auth_flow.py    ◄── 009
│   └── test_task_flow.py    ◄── 009
└── e2e/                     ◄── 014
    └── test_full_flow.py
```

---

## 6. Skill-to-Feature Mapping

| Skill | Feature | Agent |
|-------|---------|-------|
| password_hashing | 005 ✓ | AuthAgent |
| token_generation | 006 | AuthAgent |
| token_validation | 006 | AuthAgent |
| rate_limiting | 006 | AuthAgent |
| session_management | 006 | AuthAgent |
| task_creation | 007 | TaskAgent |
| task_retrieval | 007 | TaskAgent |
| task_update | 007 | TaskAgent |
| task_deletion | 007 | TaskAgent |
| ownership_validation | 007 | TaskAgent |
| user_creation | 006 | UserAgent |
| user_retrieval | 008 | UserAgent |
| email_validation | 006 | UserAgent |
| account_deletion | 008 | UserAgent |
| suggestion_generation | 010 | AIAgent |
| priority_analysis | 010 | AIAgent |
| graceful_degradation | 010 | AIAgent |

---

## 7. Next Steps

### Immediate (Unblocked)

1. **006-auth-endpoints**: Login, register, token refresh APIs
2. **007-task-endpoints**: Task CRUD APIs
3. **011-frontend-scaffold**: Next.js project setup (parallel)

### Blocked

| Feature | Blocked By | Notes |
|---------|------------|-------|
| 008 | 005 | Ready to start |
| 009 | 006, 007, 008 | Needs all APIs |
| 010 | 009 | AI integration |
| 012 | 006, 011 | Auth UI needs backend + frontend |
| 013 | 007, 012 | Task UI needs backend + auth |
| 014 | 012, 013 | E2E needs full frontend |
| 015 | 014 | Deploy needs E2E passing |

---

## 8. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-14 | Initial task graph |
