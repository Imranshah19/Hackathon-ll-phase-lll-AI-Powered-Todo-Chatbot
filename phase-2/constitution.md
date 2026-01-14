# Phase 2 Constitution

**Project**: Todo Full-Stack Web Application
**Phase**: 2 — System Design & Architecture
**Created**: 2026-01-12
**Extends**: `.specify/memory/constitution.md` v1.0.0

---

## Overview

This document extends the project constitution with Phase 2-specific principles and constraints. The base constitution remains authoritative; this document adds phase-specific clarifications.

## Inherited Principles

The following principles from the base constitution apply without modification:

| # | Principle | Status |
|---|-----------|--------|
| I | Spec-First Development | Active |
| II | Layered Architecture | Active |
| III | Test-First Development (TDD) | Active |
| IV | Secure by Design | Active |
| V | API-First Integration | Active |
| VI | Minimal Viable Diff | Active |

## Phase 2 Specific Constraints

### P2-001: Data Schema Stability

Once schemas are implemented and tested, field removal requires:
1. Deprecation notice in spec
2. Migration plan
3. Minimum 1 version grace period

**Rationale**: Prevents breaking changes to API contracts and database migrations.

### P2-002: Agent Isolation

Each agent operates with clearly defined:
- Inputs (typed schemas)
- Outputs (typed schemas)
- Failure modes (enumerated)
- Skills (assigned capabilities)

Agents MUST NOT share mutable state directly. All inter-agent communication uses the defined protocol.

**Rationale**: Enables independent testing, deployment, and reasoning about system behavior.

### P2-003: Skill Contracts

Every skill MUST define:
- Input schema (typed)
- Output schema (typed)
- Success criteria (measurable)
- Failure modes (exhaustive)

Skills with undefined behavior are prohibited.

**Rationale**: Ensures predictable behavior and comprehensive error handling.

### P2-004: Graceful Degradation

Optional features (AI suggestions) MUST NOT break core functionality when unavailable.

- Core CRUD operations: MUST work without AI
- AI features: MAY return empty results on failure
- Error propagation: MUST NOT cascade to unrelated features

**Rationale**: Ensures system reliability regardless of external service availability.

### P2-005: Multi-User Isolation

All data operations MUST be scoped to the authenticated user:
- Tasks: `WHERE user_id = current_user.id`
- User data: Only own profile accessible
- Admin operations: Explicitly flagged and audited

Cross-user data access is a security incident.

**Rationale**: Fundamental security requirement for multi-user applications.

## Technology Constraints

### Database

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Primary Keys | UUID v4 | Distributed generation, no collisions |
| Timestamps | UTC with timezone | Consistent global time handling |
| Soft Delete | Not in Phase 2 | Simplicity; add in Phase 3 if needed |
| Migrations | Alembic | SQLAlchemy-compatible, reversible |

### Authentication

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Password Hashing | Argon2id | OWASP recommended, memory-hard |
| Token Format | JWT (HS256/RS256) | Stateless, widely supported |
| Token Expiry | 24 hours default | Balance security and UX |
| Refresh Tokens | Phase 3 | Complexity deferred |

### API Design

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Versioning | `/api/v1/` prefix | Backward compatibility |
| Error Format | RFC 7807 Problem Details | Standard, parseable |
| Pagination | Limit/Offset | Simple, sufficient for Phase 2 |
| Rate Limiting | Per-IP and per-user | Prevent abuse |

## Quality Gates (Phase 2)

### Feature Completion Criteria

- [ ] Spec.md approved
- [ ] Plan.md passes Constitution Check
- [ ] Tasks.md generated with TDD structure
- [ ] All tests pass (unit, contract, integration)
- [ ] Coverage ≥ 80% for new code
- [ ] No security vulnerabilities (OWASP Top 10)
- [ ] API contract matches OpenAPI spec
- [ ] Documentation updated

### PR Merge Requirements

- [ ] Tests pass in CI
- [ ] No linting errors
- [ ] Constitution compliance verified
- [ ] At least one approval
- [ ] No unresolved comments

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial Phase 2 constitution |

---

**Reference**: [Base Constitution](../.specify/memory/constitution.md)
