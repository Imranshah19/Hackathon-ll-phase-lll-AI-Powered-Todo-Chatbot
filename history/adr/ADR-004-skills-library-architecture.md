# ADR-004: Skills Library Architecture

> **Scope**: Skills framework design - registry pattern, categorization, execution model

- **Status:** Accepted
- **Date:** 2026-01-29
- **Feature:** 003-skills-library-phase2
- **Context:** The application requires a modular, extensible system of atomic capabilities (skills) that can be composed by agents. Skills must have typed contracts, defined failure modes, and support independent testing.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - defines extensibility pattern
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - monolithic vs microservices
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - foundation for all agent operations
-->

## Decision

Adopt a **registry-based skills architecture** with the following design:

- **Skill Count**: 27 atomic skills across 7 categories
- **Categories**: Orchestration, Authentication, Task Management, User Management, AI, Planning, Execution
- **Base Pattern**: Abstract `BaseSkill` class with typed inputs/outputs
- **Discovery**: `SkillRegistry` for dynamic skill registration and lookup
- **Execution**: `SkillExecutor` with timeout handling (30s default)
- **Validation**: Pydantic schemas for input/output contracts
- **Failure Modes**: Defined taxonomy with structured error responses

**Skill Structure**:
```
backend/src/services/skills/
├── base.py           # BaseSkill abstract class
├── registry.py       # Skill discovery and registration
├── executor.py       # Skill execution engine
├── orchestration/    # Category: workflow skills
├── auth/             # Category: authentication skills
├── task/             # Category: task management skills
└── ...               # Other categories
```

## Consequences

### Positive

- **Modularity**: Skills can be developed, tested, and deployed independently
- **Composability**: Agents can combine skills for complex operations
- **Type Safety**: Pydantic contracts ensure valid inputs/outputs
- **Testability**: Each skill can be unit tested in isolation
- **Extensibility**: New skills added without modifying existing code

### Negative

- **Coordination Overhead**: 27 skills require careful dependency management
- **Learning Curve**: Developers must understand skill contracts
- **Registry Complexity**: Dynamic discovery adds runtime indirection
- **Performance**: Validation overhead on every skill invocation

## Alternatives Considered

**Alternative A: Monolithic Service Layer**
- Single service with methods for each operation
- Rejected: Poor testability, tight coupling, difficult to extend

**Alternative B: Microservices per Category**
- Separate services for auth, tasks, etc.
- Rejected: Excessive complexity for current scale, network overhead

**Alternative C: Event-Driven Skills**
- Skills communicate via message queue
- Rejected: Adds infrastructure complexity, not needed for sync operations

## References

- Feature Spec: [specs/003-skills-library-phase2/spec.md](../../specs/003-skills-library-phase2/spec.md)
- Implementation Plan: [specs/003-skills-library-phase2/plan.md](../../specs/003-skills-library-phase2/plan.md)
- API Contract: [specs/003-skills-library-phase2/contracts/skills-api.yaml](../../specs/003-skills-library-phase2/contracts/skills-api.yaml)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Principle II: Layered Architecture)
