<!--
Sync Impact Report
==================
Version change: n/a → 1.0.0 (initial ratification)
Modified principles: n/a (new constitution)
Added sections:
  - Core Principles (6 principles)
  - Technology Stack
  - Development Workflow
  - Governance
Removed sections: n/a
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ compatible (Constitution Check section present)
  - .specify/templates/spec-template.md ✅ compatible (requirements structure aligned)
  - .specify/templates/tasks-template.md ✅ compatible (phase structure supports TDD)
Follow-up TODOs: none
-->

# Todo App Constitution — Phase II Extension

## Core Principles

### I. Spec-First Development

All implementation MUST be preceded by specification artifacts. Code generation occurs exclusively through Spec-Kit + Claude Code tooling.

- Specifications MUST exist before any code is written
- Manual coding is prohibited; all code is generated from specs
- Changes to implementation require corresponding spec updates
- Spec artifacts include: spec.md, plan.md, tasks.md, contracts/

**Rationale**: Ensures traceability, consistency, and enables AI-assisted development while maintaining architectural integrity.

### II. Layered Architecture

The system MUST maintain clean separation between architectural layers with no cross-layer dependencies that bypass interfaces.

| Layer | Technology | Responsibility |
|-------|------------|----------------|
| Presentation | Next.js (App Router) | Web UI, user interaction |
| Application | FastAPI | Business logic, API endpoints |
| Data | PostgreSQL (Neon Serverless) | Persistence via SQLModel ORM |
| Auth | Better Auth + JWT | Authentication, authorization |

- Each layer communicates only through defined interfaces (REST API)
- Frontend MUST NOT directly access database
- Backend MUST be stateless; session state lives in JWT tokens
- ORM layer abstracts all database operations

**Rationale**: Enables independent scaling, testing, and replacement of components.

### III. Test-First Development (NON-NEGOTIABLE)

All features MUST follow Test-Driven Development (TDD) methodology.

- Tests are written FIRST and MUST fail before implementation
- Red-Green-Refactor cycle is strictly enforced
- Contract tests validate API boundaries
- Integration tests verify cross-layer communication
- No code merges without passing test suite

**Rationale**: Ensures correctness, provides living documentation, and enables safe refactoring.

### IV. Secure by Design

Security MUST be built into every layer, not added as an afterthought.

- JWT-based authentication for all protected endpoints
- Multi-user task isolation: users MUST NOT access other users' data
- Secrets and tokens stored in environment variables (`.env`), never hardcoded
- All inputs validated and sanitized at API boundaries
- HTTPS required for all production traffic

**Rationale**: Protects user data and ensures compliance with security best practices.

### V. API-First Integration

REST API contracts define all communication between frontend and backend.

- OpenAPI/Swagger specifications document all endpoints
- Contracts are versioned and backward-compatible where possible
- Breaking changes require major version bumps and migration plans
- Error responses follow consistent taxonomy with proper HTTP status codes

**Rationale**: Enables parallel frontend/backend development and clear interface boundaries.

### VI. Minimal Viable Diff

Every change MUST be the smallest possible modification to achieve the goal.

- No speculative features (YAGNI principle)
- No refactoring of unrelated code
- One concern per commit
- Complexity MUST be justified in plan.md if Constitution Check is violated

**Rationale**: Reduces risk, simplifies reviews, and maintains focus on delivery.

## Technology Stack

| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| Frontend Framework | Next.js | App Router, React Server Components |
| Backend Framework | FastAPI | Python async API |
| Database | PostgreSQL | Neon Serverless |
| ORM | SQLModel | Type-safe Python ORM |
| Authentication | Better Auth | JWT token-based |
| API Protocol | REST | JSON payloads |
| Testing (Backend) | pytest | Contract + Integration tests |
| Testing (Frontend) | Jest/Vitest | Component + E2E tests |

### Project Structure

```text
backend/
├── src/
│   ├── models/       # SQLModel entities
│   ├── services/     # Business logic
│   ├── api/          # FastAPI routes
│   └── auth/         # JWT/Better Auth integration
└── tests/
    ├── contract/     # API contract tests
    ├── integration/  # Cross-layer tests
    └── unit/         # Isolated unit tests

frontend/
├── src/
│   ├── app/          # Next.js App Router pages
│   ├── components/   # React components
│   └── services/     # API client services
└── tests/
    ├── component/    # Component tests
    └── e2e/          # End-to-end tests
```

## Development Workflow

### Spec-to-Implementation Flow

1. **Specify** (`/sp.specify`): Define feature requirements in spec.md
2. **Plan** (`/sp.plan`): Create architectural plan in plan.md
3. **Tasks** (`/sp.tasks`): Generate implementation tasks in tasks.md
4. **Implement** (`/sp.implement`): Execute tasks following TDD

### Quality Gates

- [ ] Spec.md exists and is approved
- [ ] Plan.md passes Constitution Check
- [ ] Tasks.md generated from plan
- [ ] Tests written and failing (Red)
- [ ] Implementation makes tests pass (Green)
- [ ] Code refactored if needed (Refactor)
- [ ] All tests pass in CI

### Branching Strategy

- `main`: Production-ready code only
- `feature/<name>`: Feature development branches
- All changes via Pull Request with passing tests

## Governance

This Constitution supersedes all other development practices for this project.

### Amendment Procedure

1. Propose change via Pull Request to constitution.md
2. Document rationale and impact assessment
3. Update version following semantic versioning:
   - **MAJOR**: Principle removal or incompatible redefinition
   - **MINOR**: New principle or section added
   - **PATCH**: Clarifications and wording improvements
4. All PRs MUST verify compliance with Constitution principles

### Compliance Review

- Every PR reviewer MUST check Constitution alignment
- Complexity violations MUST be documented in plan.md
- ADRs capture significant architectural decisions

**Version**: 1.0.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-01-12
