# Implementation Plan: Task Graph

**Branch**: `004-task-graph-phase2` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-task-graph-phase2/spec.md`

## Summary

Implement task dependency management and graph visualization for the Todo application. Users can define directed dependencies between tasks, view their task relationships as an interactive graph, and receive recommended completion orders based on topological sorting. The feature adds a new `task_dependencies` table to PostgreSQL and uses React Flow for frontend visualization.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/Next.js (frontend)
**Primary Dependencies**: FastAPI, SQLModel, React Flow, Pydantic
**Storage**: PostgreSQL (Neon Serverless) - new `task_dependencies` table
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Web application (Linux server + browser)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Graph render <2s for 100 tasks, cycle detection <500ms for 500 tasks
**Constraints**: Max 500 tasks per user, single-user graphs only (no sharing)
**Scale/Scope**: Extension to existing task management, 5 user stories, 15 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-First Development | ✅ PASS | spec.md created and approved before plan |
| II. Layered Architecture | ✅ PASS | API endpoints in FastAPI, visualization in Next.js, data in PostgreSQL |
| III. Test-First Development | ✅ PASS | TDD enforced via tasks.md structure (tests before implementation) |
| IV. Secure by Design | ✅ PASS | User-scoped dependencies (FR-014), ownership validation on all operations |
| V. API-First Integration | ✅ PASS | OpenAPI contract in contracts/task-graph-api.yaml |
| VI. Minimal Viable Diff | ✅ PASS | Single new table, extends existing Task model, no refactoring |

**Gate Status**: ✅ ALL GATES PASS — Proceed to implementation

## Project Structure

### Documentation (this feature)

```text
specs/004-task-graph-phase2/
├── plan.md              # This file
├── research.md          # Technology decisions and rationale
├── data-model.md        # TaskDependency entity and queries
├── quickstart.md        # User guide and validation scenarios
├── contracts/
│   └── task-graph-api.yaml  # OpenAPI 3.1 specification
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── task_dependency.py    # TaskDependency SQLModel
│   ├── services/
│   │   └── graph/
│   │       ├── __init__.py
│   │       ├── dependency.py     # CRUD operations
│   │       ├── cycle_detection.py # DFS cycle detection
│   │       └── topological.py    # Kahn's algorithm
│   └── api/
│       └── graph.py              # Graph endpoints
└── tests/
    ├── contract/
    │   └── graph/                # API contract tests
    ├── integration/
    │   └── graph/                # Cross-layer tests
    └── unit/
        └── graph/                # Algorithm tests

frontend/
├── src/
│   ├── app/
│   │   └── graph/
│   │       └── page.tsx          # Graph view page
│   ├── components/
│   │   └── graph/
│   │       ├── TaskGraph.tsx     # React Flow wrapper
│   │       ├── TaskNode.tsx      # Custom node component
│   │       └── GraphControls.tsx # Zoom/filter controls
│   └── services/
│       └── graph-api.ts          # API client
└── tests/
    └── components/
        └── graph/                # Component tests
```

**Structure Decision**: Web application (Option 2). Backend handles all graph algorithms and persistence. Frontend provides interactive visualization using React Flow. This matches the existing project structure from constitution.

## Complexity Tracking

> No Constitution Check violations. No complexity justification needed.

## Research Summary

See [research.md](./research.md) for full details.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Graph storage | Adjacency list in PostgreSQL | Simple, efficient for sparse graphs |
| Cycle detection | DFS on write | O(V+E), synchronous validation |
| Visualization | React Flow | React-native, built-in zoom/pan |
| Sorting algorithm | Kahn's algorithm | Identifies parallel groups |
| API structure | Nested REST resources | RESTful, clear authorization scope |
| Layout persistence | Computed (not stored) | Simpler model, consistent after changes |

## Data Model Summary

See [data-model.md](./data-model.md) for full details.

**New Entity**: `TaskDependency`
- `id`: UUID (PK)
- `source_task_id`: UUID (FK → Task) - prerequisite
- `target_task_id`: UUID (FK → Task) - dependent
- `user_id`: UUID (FK → User) - denormalized for queries
- `created_at`: DateTime

**Constraints**: Unique(source, target), no self-loops, no cycles

## API Summary

See [contracts/task-graph-api.yaml](./contracts/task-graph-api.yaml) for full OpenAPI spec.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tasks/{id}/dependencies` | GET | List prerequisites and dependents |
| `/tasks/{id}/dependencies` | POST | Create dependency |
| `/tasks/{id}/dependencies/{dep_id}` | DELETE | Remove dependency |
| `/tasks/graph` | GET | Full graph for user |
| `/tasks/graph/recommended-order` | GET | Topological sort |
| `/tasks/graph/validate` | POST | Check if dependency is valid |

## Next Steps

Run `/sp.tasks` to generate implementation tasks following TDD methodology.
