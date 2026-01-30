# ADR-002: Backend Technology Stack

> **Scope**: Core backend technologies for all phases - framework, ORM, database, security

- **Status:** Accepted
- **Date:** 2026-01-29
- **Feature:** 005-data-schemas-phase2, Cross-cutting
- **Context:** The Todo application requires a modern, type-safe backend stack that supports async operations, clean ORM patterns, and serverless database deployment. The stack must be maintainable by AI-assisted development workflows.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - foundation for all phases
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Django, Flask options evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - affects all backend code
-->

## Decision

Adopt the following **backend technology stack**:

- **Web Framework**: FastAPI (Python 3.11+)
  - Async-first, automatic OpenAPI generation, Pydantic validation
- **ORM**: SQLModel
  - Type-safe, combines SQLAlchemy + Pydantic, reduces boilerplate
- **Database**: PostgreSQL via Neon Serverless
  - Managed, auto-scaling, branching for development
- **Password Hashing**: Argon2id (via argon2-cffi)
  - OWASP recommended, memory-hard, side-channel resistant
- **Authentication**: Better Auth + JWT
  - Stateless tokens, compatible with Next.js frontend
- **Testing**: pytest + pytest-asyncio
  - Contract, integration, and unit test support

## Consequences

### Positive

- **Type Safety**: End-to-end type checking from DB to API
- **Developer Experience**: Auto-generated docs, fast iteration
- **Performance**: Async support for concurrent requests
- **AI-Friendly**: Clean patterns that AI code generation handles well
- **Serverless Ready**: Neon scales automatically, no connection pooling complexity

### Negative

- **SQLModel Maturity**: Newer than SQLAlchemy, fewer community examples
- **Neon Lock-in**: Serverless PostgreSQL less portable than self-hosted
- **Async Complexity**: Requires async-aware testing and debugging
- **Python GIL**: CPU-bound operations may need worker processes

## Alternatives Considered

**Alternative A: Django + Django ORM + MySQL**
- Full-featured framework with admin panel
- Rejected: Heavier, synchronous by default, less type-safe

**Alternative B: Flask + SQLAlchemy + PostgreSQL**
- Lightweight, mature ecosystem
- Rejected: More boilerplate, no built-in async, manual schema validation

**Alternative C: Express.js + Prisma + PostgreSQL**
- JavaScript ecosystem, excellent TypeScript support
- Rejected: Team preference for Python, better AI integration with FastAPI

## References

- Feature Spec: [specs/005-data-schemas-phase2/spec.md](../../specs/005-data-schemas-phase2/spec.md)
- Implementation Plan: [specs/005-data-schemas-phase2/plan.md](../../specs/005-data-schemas-phase2/plan.md)
- Research: [specs/005-data-schemas-phase2/research.md](../../specs/005-data-schemas-phase2/research.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Section: Technology Stack)
