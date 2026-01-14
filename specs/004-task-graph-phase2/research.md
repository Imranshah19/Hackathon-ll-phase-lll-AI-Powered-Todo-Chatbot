# Research: Task Graph Phase-2

**Feature**: 004-task-graph-phase2
**Date**: 2026-01-12
**Status**: Complete

## Research Questions

### RQ-001: Graph Data Structure for Dependencies

**Question**: What is the best approach for storing and managing task dependencies as a directed acyclic graph (DAG)?

**Decision**: Adjacency list representation stored in a dedicated `task_dependencies` database table with `source_task_id` and `target_task_id` foreign keys.

**Rationale**:
- Simple to implement with relational database
- Efficient for sparse graphs (most tasks have few dependencies)
- Easy to query for both predecessors and successors
- Supports efficient cycle detection via DFS

**Alternatives Considered**:
- Adjacency matrix: Rejected - space inefficient for sparse graphs, complex schema changes
- Graph database (Neo4j): Rejected - over-engineered for single-user task graphs, adds infrastructure complexity
- JSON field in task record: Rejected - hard to query, referential integrity issues

---

### RQ-002: Cycle Detection Algorithm

**Question**: How should the system detect and prevent circular dependencies?

**Decision**: Depth-First Search (DFS) cycle detection performed on write operations (create/update dependency).

**Rationale**:
- O(V+E) complexity is acceptable for user-scale graphs (max 500 tasks)
- Can be performed synchronously during API request
- Returns immediately on first cycle found with clear error path

**Alternatives Considered**:
- Topological sort attempt: Similar complexity, less intuitive error reporting
- Transitive closure table: Fast lookups but expensive maintenance on updates
- Client-side validation only: Rejected - cannot trust client for data integrity

---

### RQ-003: Frontend Graph Visualization Library

**Question**: Which library should be used for rendering the interactive task graph in Next.js?

**Decision**: React Flow (reactflow.dev) - purpose-built for node-based graphs in React.

**Rationale**:
- Native React component model, excellent TypeScript support
- Built-in zoom/pan, node dragging, edge rendering
- Extensive customization for node appearance
- Active maintenance and large community
- MIT license

**Alternatives Considered**:
- D3.js: Powerful but low-level, requires significant integration work for React
- Cytoscape.js: More academic/scientific focus, heavier bundle size
- vis.js: Less React-native, older API patterns
- Custom canvas/SVG: Maximum control but high development cost

---

### RQ-004: Topological Sort for Recommended Order

**Question**: What algorithm should be used to generate the recommended task completion order?

**Decision**: Kahn's algorithm for topological sorting, extended to identify parallel execution opportunities.

**Rationale**:
- Produces deterministic ordering
- Naturally identifies tasks with no remaining dependencies (parallelizable)
- O(V+E) complexity
- Clear failure mode when cycles exist (though prevented at write time)

**Alternatives Considered**:
- DFS-based topological sort: Similar complexity, less intuitive for parallel identification
- Critical path method (CPM): Over-engineered without duration estimates per task

---

### RQ-005: API Design for Dependency Operations

**Question**: How should the REST API be structured for dependency CRUD operations?

**Decision**: Nested resource under tasks with dedicated dependency endpoints.

```
POST   /api/v1/tasks/{task_id}/dependencies          # Add dependency
GET    /api/v1/tasks/{task_id}/dependencies          # List dependencies
DELETE /api/v1/tasks/{task_id}/dependencies/{dep_id} # Remove dependency
GET    /api/v1/tasks/graph                           # Full graph for user
GET    /api/v1/tasks/graph/recommended-order         # Topological sort
```

**Rationale**:
- RESTful resource hierarchy (dependencies belong to tasks)
- Clear ownership and authorization scope
- Separates graph-wide operations from per-task operations

**Alternatives Considered**:
- Flat `/api/v1/dependencies` resource: Less intuitive, harder to scope authorization
- GraphQL: Constitution specifies REST API-first

---

### RQ-006: Graph State Persistence

**Question**: Should graph layout positions be persisted or computed on each render?

**Decision**: Computed on each render using automatic layout algorithm (dagre/ELK via React Flow).

**Rationale**:
- Simpler data model (no position storage)
- Consistent layout after graph modifications
- Reduces API payload size
- Users can still interact (drag nodes) for session

**Alternatives Considered**:
- Persist positions: Adds complexity, positions become stale after graph changes
- Hybrid (save only manual adjustments): Complex to merge automatic and manual layouts

---

## Technology Decisions Summary

| Area | Decision | Confidence |
|------|----------|------------|
| Backend storage | PostgreSQL table `task_dependencies` | High |
| Cycle detection | DFS on write | High |
| Frontend visualization | React Flow | High |
| Sorting algorithm | Kahn's algorithm | High |
| API style | Nested REST resources | High |
| Layout persistence | Computed (not persisted) | Medium |

## Open Questions (None)

All research questions resolved. Ready for Phase 1 design.
