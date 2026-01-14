# Quickstart: Task Graph Feature

**Feature**: 004-task-graph-phase2
**Date**: 2026-01-12

## Overview

This guide explains how to use the Task Graph feature to manage task dependencies and visualize your workflow.

## Prerequisites

- Authenticated user account
- At least 2 existing tasks

## Core Workflows

### 1. Create a Task Dependency

**Scenario**: Task B cannot start until Task A is complete.

1. Navigate to Task B details
2. Click "Add Prerequisite"
3. Select Task A from the list
4. Confirm the dependency

**Result**: Task B now shows Task A as a prerequisite. Task B will be marked as "blocked" until Task A is completed.

**API Example**:
```bash
curl -X POST /api/v1/tasks/{task_b_id}/dependencies \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"source_task_id": "{task_a_id}"}'
```

---

### 2. View Task Graph

**Scenario**: Visualize all tasks and their dependencies.

1. Navigate to Dashboard
2. Click "Graph View" tab
3. Use mouse wheel to zoom, drag to pan
4. Hover over nodes for task details
5. Click nodes to edit tasks

**Visual Guide**:
- **Circles**: Task nodes
- **Arrows**: Dependencies (points from prerequisite to dependent)
- **Green nodes**: Completed tasks
- **Yellow nodes**: Ready to start (no blockers)
- **Gray nodes**: Blocked (has incomplete prerequisites)

---

### 3. Get Recommended Order

**Scenario**: Determine the optimal sequence for completing tasks.

1. In Graph View, click "Recommended Order"
2. View tasks grouped by dependency level
3. Tasks at the same level can be done in parallel

**API Example**:
```bash
curl /api/v1/tasks/graph/recommended-order \
  -H "Authorization: Bearer {token}"
```

**Response**:
```json
{
  "levels": [
    {"level": 0, "tasks": ["Setup environment"], "can_parallelize": true},
    {"level": 1, "tasks": ["Install dependencies", "Create config"], "can_parallelize": true},
    {"level": 2, "tasks": ["Run tests"], "can_parallelize": true}
  ]
}
```

---

### 4. Remove a Dependency

**Scenario**: Task B no longer needs Task A to be complete first.

1. Navigate to Task B details
2. Find Task A in prerequisites list
3. Click "Remove" next to Task A
4. Confirm removal

**API Example**:
```bash
curl -X DELETE /api/v1/tasks/{task_b_id}/dependencies/{dependency_id} \
  -H "Authorization: Bearer {token}"
```

---

### 5. Filter Graph View

**Scenario**: Focus on incomplete tasks only.

1. In Graph View, click "Filters"
2. Select "Incomplete only"
3. Graph updates to show only relevant tasks

**Focus Mode**:
1. Right-click a task node
2. Select "Focus on this task"
3. View only this task, its prerequisites, and its dependents

---

## Edge Cases

### Circular Dependency Prevention

If you try to create a dependency that would form a cycle (A→B→C→A), the system will:
- Reject the operation
- Show an error message explaining the cycle
- Provide the path of the cycle

### Completing a Blocked Task

If you try to complete a task that has incomplete prerequisites:
- You'll see a warning dialog
- Prerequisites are listed
- You can proceed anyway or cancel

### Deleting a Task with Dependents

If you try to delete a task that other tasks depend on:
- You'll see a warning with the count of affected tasks
- Dependents are listed
- Confirm to delete (dependencies are removed)
- Cancel to keep the task

---

## Validation Scenarios

### Test: Basic Dependency Creation

```
Given: Tasks "Write code" and "Write tests" exist
When: I add "Write code" as prerequisite of "Write tests"
Then: "Write tests" shows "Write code" as prerequisite
And: Graph shows arrow from "Write code" to "Write tests"
```

### Test: Cycle Prevention

```
Given: Dependency "A→B" exists
When: I try to create dependency "B→A"
Then: System rejects with "Circular dependency detected"
And: Shows cycle path: A → B → A
```

### Test: Recommended Order

```
Given: Tasks A, B, C with dependencies A→B, A→C
When: I request recommended order
Then: Level 0 contains A
And: Level 1 contains B and C (parallelizable)
```

---

## Performance Notes

- Graph renders within 2 seconds for up to 100 tasks
- Cycle detection completes within 500ms for up to 500 tasks
- Recommended order calculation completes within 1 second for up to 200 tasks

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't see graph | Ensure you have at least one task |
| Dependency not showing | Refresh the page, check filters |
| Graph is cluttered | Use Focus mode or status filters |
| Performance slow | Filter to reduce visible tasks |
