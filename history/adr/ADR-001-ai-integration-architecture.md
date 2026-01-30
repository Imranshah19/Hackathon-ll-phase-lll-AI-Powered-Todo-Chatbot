# ADR-001: AI Integration Architecture

> **Scope**: Phase 3 AI integration approach - interpreter-only pattern with graceful degradation

- **Status:** Accepted
- **Date:** 2026-01-29
- **Feature:** 006-ai-chat
- **Context:** Phase 3 requires natural language task management while maintaining backward compatibility with Phase 2 CLI. The AI layer must interpret user intent without directly modifying data, ensuring auditability and preventing AI-induced data corruption.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - defines AI/system boundary
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - direct execution vs interpreter
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - affects all AI interactions
-->

## Decision

Adopt an **AI-as-Interpreter architecture** where AI components only translate natural language to structured commands:

- **AI Provider**: Claude API (primary) with OpenAI fallback
- **Agents Framework**: OpenAI Agents SDK for orchestration
- **MCP Integration**: Official MCP SDK for Model Context Protocol
- **NLP Layer**: Custom interpreter for intent extraction and slot filling
- **Execution Engine**: Phase 2 Bonsai CLI (unchanged)
- **State Management**: Stateless AI chat layer - no AI-owned state

**Flow**: User → NLP Interpreter → SP.Plan Generator → Constitution Validation → Bonsai CLI → Database

## Consequences

### Positive

- **Auditability**: All executions pass through validated CLI commands
- **Safety**: AI cannot directly corrupt data; execution layer enforces constraints
- **Backward Compatibility**: Phase 2 CLI remains the single execution path
- **Testability**: AI interpretation and CLI execution can be tested independently
- **Debuggability**: Generated commands are human-readable and reproducible

### Negative

- **Latency**: Additional interpretation step adds ~1-2s to response time
- **Capability Ceiling**: Complex operations limited by CLI command vocabulary
- **Error Surface**: Interpretation errors require sophisticated error handling
- **Dual Maintenance**: CLI commands and NLP patterns must stay synchronized

## Alternatives Considered

**Alternative A: Direct AI Execution**
- AI directly calls database/services without CLI intermediary
- Rejected: Violates auditability principle, increases data corruption risk

**Alternative B: LangChain-based Architecture**
- Use LangChain for agent orchestration
- Rejected: Adds complexity; OpenAI Agents SDK better fits our stateless model

**Alternative C: Monolithic AI Service**
- Single service handles NLP, planning, and execution
- Rejected: Violates layered architecture, makes testing difficult

## References

- Feature Spec: [specs/006-ai-chat/spec.md](../../specs/006-ai-chat/spec.md)
- Implementation Plan: [specs/006-ai-chat/plan.md](../../specs/006-ai-chat/plan.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Principle VII)
- Related ADRs: ADR-005 (Graceful Degradation Strategy)
