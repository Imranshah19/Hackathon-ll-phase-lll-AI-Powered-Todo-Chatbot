# ADR-003: Frontend Technology Stack

> **Scope**: Core frontend technologies - framework, routing, styling, visualization

- **Status:** Accepted
- **Date:** 2026-01-29
- **Feature:** 004-task-graph-phase2, 006-ai-chat
- **Context:** The Todo application requires a modern React-based frontend that supports server-side rendering, type safety, and complex UI components like chat interfaces and graph visualization.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - defines all UI architecture
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Remix, Vue evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - affects all frontend code
-->

## Decision

Adopt the following **frontend technology stack**:

- **Framework**: Next.js 14+ with App Router
  - Server components, streaming, built-in routing
- **Language**: TypeScript 5.x
  - Type safety, better IDE support, fewer runtime errors
- **Graph Visualization**: React Flow
  - React-native, built-in zoom/pan, custom node support
- **Testing**: Jest/Vitest + React Testing Library
  - Component and E2E test coverage
- **State Management**: React Context (start simple)
  - Avoid premature optimization, add Redux/Zustand if needed

## Consequences

### Positive

- **Performance**: Server components reduce client-side JavaScript
- **SEO Ready**: SSR support out of the box
- **Type Safety**: Full TypeScript support throughout
- **Rich Ecosystem**: Extensive component libraries available
- **Vercel Optimized**: First-class deployment support

### Negative

- **App Router Learning Curve**: Newer paradigm, fewer tutorials
- **Bundle Size**: React Flow adds ~150KB to visualization pages
- **Server/Client Boundary**: Requires careful component architecture
- **Hydration Complexity**: SSR/CSR mismatch can cause bugs

## Alternatives Considered

**Alternative A: Remix + styled-components**
- Strong data loading patterns, good DX
- Rejected: Smaller ecosystem, less visualization library support

**Alternative B: Vue 3 + Nuxt + D3.js**
- Excellent reactivity, smaller bundle
- Rejected: Team expertise in React, D3 has steeper learning curve than React Flow

**Alternative C: Angular + NgRx + ECharts**
- Enterprise-ready, opinionated structure
- Rejected: Heavier framework, longer development cycles

## References

- Feature Spec: [specs/004-task-graph-phase2/spec.md](../../specs/004-task-graph-phase2/spec.md)
- Implementation Plan: [specs/004-task-graph-phase2/plan.md](../../specs/004-task-graph-phase2/plan.md)
- Research: [specs/004-task-graph-phase2/research.md](../../specs/004-task-graph-phase2/research.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Section: Technology Stack)
