# ADR-005: Graceful Degradation Strategy

> **Scope**: AI failure handling - timeout policy, fallback modes, reliability guarantees

- **Status:** Accepted
- **Date:** 2026-01-29
- **Feature:** 006-ai-chat
- **Context:** AI services are inherently unreliable (network issues, rate limits, model unavailability). The system must maintain core functionality when AI features fail, ensuring users can always manage their tasks.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - defines reliability model
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - queue-based, retry patterns
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - affects all AI interactions
-->

## Decision

Implement a **graceful degradation strategy** with the following policies:

- **AI Timeout**: 5 seconds maximum for any AI operation
- **Fallback Mode**: CLI command input available when AI fails
- **Stateless Chat**: No AI-owned state that could become inconsistent
- **Error Taxonomy**: Structured error responses with recovery guidance
- **Logging**: All AI failures logged with context for debugging

**Degradation Levels**:
1. **Normal**: AI interprets and generates commands
2. **Degraded**: AI timeout → prompt user for CLI command
3. **Offline**: AI service down → full CLI mode with clear messaging

**Frontend Fallback UI**:
- `FallbackCLI.tsx` component for manual command entry
- Clear indication when operating in degraded mode
- One-click retry for failed AI operations

## Consequences

### Positive

- **Reliability**: Core CRUD operations always available
- **User Trust**: Predictable behavior during failures
- **Debugging**: Comprehensive failure logging
- **Testing**: Fallback paths can be explicitly tested
- **Recovery**: Users can complete tasks without waiting for AI

### Negative

- **UX Complexity**: Users must understand two interaction modes
- **Development Cost**: Fallback UI requires additional implementation
- **Timeout Tuning**: 5s may be too short/long for different operations
- **State Sync**: Must ensure CLI fallback actions sync with conversation history

## Alternatives Considered

**Alternative A: No Fallback (AI Required)**
- Simpler implementation, single interaction mode
- Rejected: Violates reliability principle, poor UX during outages

**Alternative B: Queue-Based Retry**
- Failed AI requests queued for retry when service recovers
- Rejected: Adds complexity, users expect immediate feedback for task operations

**Alternative C: Multiple AI Provider Failover**
- Automatic failover between Claude/OpenAI/local models
- Rejected: Added complexity; 5s timeout + CLI fallback is simpler and sufficient

## References

- Feature Spec: [specs/006-ai-chat/spec.md](../../specs/006-ai-chat/spec.md)
- Implementation Plan: [specs/006-ai-chat/plan.md](../../specs/006-ai-chat/plan.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Principle X: Graceful AI Degradation)
- Related ADRs: ADR-001 (AI Integration Architecture)
