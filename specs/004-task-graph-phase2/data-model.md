# Data Model: Task Graph Phase-2

**Feature**: 004-task-graph-phase2
**Date**: 2026-01-12
**Status**: Complete

## Entities

### TaskDependency

Represents a directed edge in the task graph where one task must be completed before another.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| source_task_id | UUID | FK → Task.id, NOT NULL | Task that must be completed first (prerequisite) |
| target_task_id | UUID | FK → Task.id, NOT NULL | Task that depends on source (blocked task) |
| user_id | UUID | FK → User.id, NOT NULL | Owner (denormalized for query efficiency) |
| created_at | DateTime | NOT NULL, auto | When dependency was created |

**Constraints**:
- UNIQUE(source_task_id, target_task_id) — No duplicate edges
- CHECK(source_task_id != target_task_id) — No self-loops
- Both tasks must belong to the same user (enforced at application layer)

**Indexes**:
- idx_dependency_source: (source_task_id) — Find dependents of a task
- idx_dependency_target: (target_task_id) — Find prerequisites of a task
- idx_dependency_user: (user_id) — Query all dependencies for graph view

---

### Task (Extended)

The existing Task entity from system design is extended with computed/derived properties for graph operations.

| Existing Fields | Notes |
|-----------------|-------|
| id, user_id, title, description, is_completed, created_at, updated_at | From system design spec |

**Derived Properties** (computed, not stored):
- `prerequisite_count`: Count of incomplete tasks this task depends on
- `dependent_count`: Count of tasks that depend on this task
- `is_blocked`: True if any prerequisite is incomplete
- `can_start`: True if all prerequisites are complete

---

## Relationships

```
┌──────────┐         ┌──────────────────┐         ┌──────────┐
│   User   │ 1────*  │  TaskDependency  │  *────1 │   Task   │
└──────────┘         └──────────────────┘         └──────────┘
     │                      │   │                      │
     │                      │   │                      │
     └──────────────────────┘   └──────────────────────┘
         user owns deps           source/target tasks
```

- User 1:N TaskDependency (a user owns their dependency graph)
- Task 1:N TaskDependency (as source) — Tasks I'm prerequisite for
- Task 1:N TaskDependency (as target) — Tasks that block me

---

## State Transitions

### Task Completion with Dependencies

```
[incomplete] ──────> [completed]
                         │
                         ▼
              Check: Has incomplete prerequisites?
                    /           \
                  Yes            No
                   │              │
                   ▼              ▼
            Show warning    Complete normally
            (soft block)
```

### Dependency Lifecycle

```
[none] ──create──> [active] ──delete──> [none]
                      │
                      ├── source task deleted ──> cascade delete dependency
                      └── target task deleted ──> cascade delete dependency
```

---

## Validation Rules

### On Dependency Creation

1. **Ownership**: Both source and target task must belong to requesting user
2. **Existence**: Both tasks must exist
3. **No self-loop**: source_task_id ≠ target_task_id
4. **No duplicate**: Dependency with same source/target must not exist
5. **No cycle**: Adding this edge must not create a cycle in the graph

### Cycle Detection Algorithm

```python
def would_create_cycle(graph, new_source, new_target):
    """
    DFS from new_target to see if we can reach new_source.
    If yes, adding new_source → new_target creates a cycle.
    """
    visited = set()
    stack = [new_target]

    while stack:
        node = stack.pop()
        if node == new_source:
            return True  # Cycle detected
        if node not in visited:
            visited.add(node)
            # Add all nodes that this node points to
            stack.extend(graph.get_successors(node))

    return False
```

---

## Query Patterns

### Get Full Graph for User

```sql
-- All tasks
SELECT * FROM tasks WHERE user_id = :user_id;

-- All edges
SELECT * FROM task_dependencies WHERE user_id = :user_id;
```

### Get Prerequisites for a Task

```sql
SELECT t.*
FROM tasks t
JOIN task_dependencies d ON t.id = d.source_task_id
WHERE d.target_task_id = :task_id;
```

### Get Dependents of a Task

```sql
SELECT t.*
FROM tasks t
JOIN task_dependencies d ON t.id = d.target_task_id
WHERE d.source_task_id = :task_id;
```

### Check if Task is Blocked

```sql
SELECT EXISTS (
    SELECT 1
    FROM task_dependencies d
    JOIN tasks t ON t.id = d.source_task_id
    WHERE d.target_task_id = :task_id
    AND t.is_completed = false
) AS is_blocked;
```

### Topological Sort (Recommended Order)

Implemented in application code using Kahn's algorithm:

```python
def topological_sort(tasks, dependencies):
    """
    Returns tasks in dependency order.
    Tasks at same level can be executed in parallel.
    """
    in_degree = {t.id: 0 for t in tasks}
    graph = {t.id: [] for t in tasks}

    for dep in dependencies:
        graph[dep.source_task_id].append(dep.target_task_id)
        in_degree[dep.target_task_id] += 1

    # Start with tasks that have no prerequisites
    queue = [t for t in tasks if in_degree[t.id] == 0]
    result = []

    while queue:
        # All tasks in current queue can run in parallel
        level = queue[:]
        queue = []
        result.append(level)

        for task in level:
            for dependent_id in graph[task.id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(next(t for t in tasks if t.id == dependent_id))

    return result  # List of levels, each level is parallelizable
```

---

## Migration Notes

- New table `task_dependencies` to be created
- No changes to existing `tasks` table schema
- Existing tasks will have empty dependency graphs (no migration of existing data needed)
