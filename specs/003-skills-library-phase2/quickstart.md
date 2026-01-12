# Quickstart: Skills Library Phase-2

**Date**: 2026-01-12
**Branch**: `003-skills-library-phase2`

---

## Overview

This guide covers how to implement and use skills in the Todo Full-Stack Web Application. Skills are atomic, reusable capabilities that agents invoke to perform specific operations.

---

## Prerequisites

- Python 3.11+
- FastAPI
- Pydantic v2
- pytest (for testing)

---

## 1. Creating a New Skill

### Step 1: Define Input/Output Schemas

```python
# backend/src/services/skills/task/schemas.py

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class TaskCreateInput(BaseModel):
    """Input schema for task_creation skill."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    priority: int = Field(1, ge=1, le=5)
    user_id: UUID

class TaskCreateOutput(BaseModel):
    """Output schema for task_creation skill."""
    task_id: UUID
    title: str
    created_at: datetime
```

### Step 2: Implement the Skill

```python
# backend/src/services/skills/task/task_creation.py

from ..base import BaseSkill, skill
from ..models import SkillResult, SkillContext, FailureCode
from .schemas import TaskCreateInput, TaskCreateOutput

@skill
class TaskCreationSkill(BaseSkill[TaskCreateInput, TaskCreateOutput]):
    """Create a new task for a user."""

    name = "task_creation"
    description = "Create a new task for a user"
    category = "task_management"
    assigned_to = ["TaskAgent"]
    failure_modes = [
        FailureCode.VALIDATION_ERROR,
        FailureCode.PERSISTENCE_ERROR,
        FailureCode.UNAUTHORIZED
    ]

    def execute(
        self,
        input: TaskCreateInput,
        context: SkillContext
    ) -> SkillResult[TaskCreateOutput]:
        """Execute task creation."""
        try:
            # Business logic here
            task = self._create_task(input)

            return SkillResult.success(
                output=TaskCreateOutput(
                    task_id=task.id,
                    title=task.title,
                    created_at=task.created_at
                ),
                context=context
            )
        except ValidationError as e:
            return SkillResult.failure(
                code=FailureCode.VALIDATION_ERROR,
                message=str(e),
                context=context
            )
        except DatabaseError as e:
            return SkillResult.failure(
                code=FailureCode.PERSISTENCE_ERROR,
                message="Failed to save task",
                context=context
            )

    def _create_task(self, input: TaskCreateInput) -> Task:
        """Internal task creation logic."""
        # Implementation
        pass
```

### Step 3: Register the Skill

The `@skill` decorator automatically registers the skill. Import it in the package `__init__.py`:

```python
# backend/src/services/skills/task/__init__.py

from .task_creation import TaskCreationSkill
from .task_retrieval import TaskRetrievalSkill
from .task_update import TaskUpdateSkill
from .task_deletion import TaskDeletionSkill
from .ownership_validation import OwnershipValidationSkill

__all__ = [
    "TaskCreationSkill",
    "TaskRetrievalSkill",
    "TaskUpdateSkill",
    "TaskDeletionSkill",
    "OwnershipValidationSkill",
]
```

---

## 2. Invoking a Skill

### From an Agent

```python
# backend/src/agents/task_agent.py

from services.skills import SkillRegistry, SkillContext
from uuid import uuid4

class TaskAgent:
    def create_task(self, user_id: UUID, title: str, **kwargs):
        # Get skill from registry
        skill = SkillRegistry.get("task_creation")

        # Create execution context
        context = SkillContext(
            correlation_id=uuid4(),
            invoking_agent="TaskAgent",
            user_id=user_id
        )

        # Execute skill
        result = skill().execute(
            TaskCreateInput(
                user_id=user_id,
                title=title,
                **kwargs
            ),
            context
        )

        if result.success:
            return result.output
        else:
            raise SkillFailure(result.failure)
```

### Via API Endpoint

```python
# backend/src/api/skills.py

from fastapi import APIRouter, Header, HTTPException
from services.skills import SkillRegistry, SkillContext, SkillExecutor
from uuid import UUID, uuid4

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.post("/{skill_name}/invoke")
async def invoke_skill(
    skill_name: str,
    payload: dict,
    x_correlation_id: UUID | None = Header(None),
    x_invoking_agent: str = Header(...),
):
    # Get skill
    skill_class = SkillRegistry.get(skill_name)
    if not skill_class:
        raise HTTPException(404, detail=f"Skill '{skill_name}' not found")

    # Create context
    context = SkillContext(
        correlation_id=x_correlation_id or uuid4(),
        invoking_agent=x_invoking_agent
    )

    # Execute with validation and observability
    executor = SkillExecutor()
    result = await executor.execute(skill_class(), payload, context)

    if result.success:
        return {
            "success": True,
            "output": result.output.model_dump(),
            "metadata": result.metadata.model_dump()
        }
    else:
        return {
            "success": False,
            "failure": result.failure.model_dump(),
            "metadata": result.metadata.model_dump()
        }
```

---

## 3. Handling Failures

### Check Recoverability

```python
result = skill.execute(input, context)

if not result.success:
    if result.failure.recoverable:
        # Can retry
        logger.warning(f"Recoverable failure: {result.failure.code}")
        return retry_with_backoff(skill, input, context)
    else:
        # Cannot retry
        logger.error(f"Fatal failure: {result.failure.code}")
        raise SkillFatalError(result.failure)
```

### Map Failure Codes to HTTP Status

```python
FAILURE_TO_HTTP: dict[FailureCode, int] = {
    FailureCode.VALIDATION_ERROR: 400,
    FailureCode.NOT_FOUND: 404,
    FailureCode.UNAUTHORIZED: 401,
    FailureCode.RATE_EXCEEDED: 429,
    FailureCode.TIMEOUT: 408,
    FailureCode.PERSISTENCE_ERROR: 500,
    FailureCode.EXTERNAL_SERVICE_ERROR: 503,
    FailureCode.INTERNAL_ERROR: 500,
}
```

---

## 4. Composing Skills

### Sequential Chain

```python
from services.skills import SkillChain

# Validate ownership, then update task
chain = (
    SkillChain()
    .then(OwnershipValidationSkill())
    .then(
        TaskUpdateSkill(),
        transform=lambda owner_result: TaskUpdateInput(
            task_id=owner_result.resource_id,
            user_id=owner_result.user_id,
            **update_data
        )
    )
)

result = chain.execute(
    OwnershipValidationInput(
        user_id=user_id,
        resource_type="task",
        resource_id=task_id
    ),
    context
)
```

### Parallel Execution

```python
from services.skills import SkillParallel

# Fetch user data and their tasks concurrently
parallel = SkillParallel([
    (UserRetrievalSkill(), UserRetrievalInput(user_id=user_id)),
    (TaskRetrievalSkill(), TaskRetrievalInput(user_id=user_id)),
])

results = await parallel.execute(context)
user_result, tasks_result = results
```

---

## 5. Testing Skills

### Unit Test Template

```python
# backend/tests/unit/skills/test_task_creation.py

import pytest
from uuid import uuid4
from services.skills.task import TaskCreationSkill
from services.skills.models import SkillContext, FailureCode

@pytest.fixture
def context():
    return SkillContext(
        correlation_id=uuid4(),
        invoking_agent="TestAgent"
    )

@pytest.fixture
def skill():
    return TaskCreationSkill()

class TestTaskCreationSkill:
    def test_creates_task_with_valid_input(self, skill, context):
        """Given valid input, skill creates task successfully."""
        input_data = TaskCreateInput(
            title="Test Task",
            user_id=uuid4()
        )

        result = skill.execute(input_data, context)

        assert result.success is True
        assert result.output.title == "Test Task"
        assert result.output.task_id is not None

    def test_fails_with_empty_title(self, skill, context):
        """Given empty title, skill returns validation error."""
        input_data = TaskCreateInput(
            title="",
            user_id=uuid4()
        )

        result = skill.execute(input_data, context)

        assert result.success is False
        assert result.failure.code == FailureCode.VALIDATION_ERROR

    def test_fails_with_invalid_priority(self, skill, context):
        """Given priority out of range, skill returns validation error."""
        with pytest.raises(ValidationError):
            TaskCreateInput(
                title="Test",
                priority=10,  # Max is 5
                user_id=uuid4()
            )
```

### Contract Test Template

```python
# backend/tests/contract/skills/test_task_creation_contract.py

import pytest
from services.skills.task import TaskCreationSkill
from services.skills.models import SkillResult

class TestTaskCreationContract:
    def test_output_schema_matches_definition(self):
        """Output schema matches skill's declared output_schema."""
        skill = TaskCreationSkill()
        output_schema = skill.output_schema()

        # Verify all declared fields are present
        assert 'task_id' in output_schema.model_fields
        assert 'title' in output_schema.model_fields
        assert 'created_at' in output_schema.model_fields

    def test_failure_modes_are_valid(self):
        """All declared failure modes are valid FailureCodes."""
        skill = TaskCreationSkill()

        for mode in skill.failure_modes:
            assert mode in FailureCode.__members__.values()

    def test_result_contains_required_metadata(self, context):
        """Skill result always contains required metadata."""
        skill = TaskCreationSkill()
        result = skill.execute(valid_input, context)

        assert result.metadata.correlation_id is not None
        assert result.metadata.duration_ms >= 0
        assert result.metadata.skill_name == "task_creation"
```

---

## 6. Skill Categories Reference

| Category | Skills | Agent |
|----------|--------|-------|
| orchestration | request_routing, workflow_coordination, response_aggregation, error_handling | OrchestratorAgent |
| authentication | password_hashing, token_generation, token_validation, rate_limiting, session_management | AuthAgent |
| task_management | task_creation, task_retrieval, task_update, task_deletion, ownership_validation | TaskAgent |
| user_management | user_creation, user_retrieval, profile_update, email_validation, account_deletion | UserAgent |
| ai | suggestion_generation, priority_analysis, category_inference, output_sanitization, graceful_degradation | AIAgent |
| planning | goal_decomposition, task_sequencing, dependency_analysis, feasibility_check, plan_optimization | PlannerAgent |
| execution | task_execution, progress_reporting, failure_handling, retry_logic, state_management | TaskExecutorAgent |

---

## 7. Common Patterns

### Ownership Validation Before Operation

```python
def update_task(user_id: UUID, task_id: UUID, data: dict):
    # First validate ownership
    ownership = OwnershipValidationSkill().execute(
        OwnershipValidationInput(
            user_id=user_id,
            resource_type="task",
            resource_id=task_id
        ),
        context
    )

    if not ownership.success or not ownership.output.is_owner:
        raise UnauthorizedError("Not task owner")

    # Then perform update
    return TaskUpdateSkill().execute(
        TaskUpdateInput(task_id=task_id, user_id=user_id, **data),
        context
    )
```

### AI Skill with Graceful Degradation

```python
def get_suggestions(user_id: UUID):
    result = SuggestionGenerationSkill().execute(
        SuggestionGenerationInput(user_id=user_id, count=3),
        context
    )

    if result.success:
        if result.metadata.get("degraded"):
            logger.warning("AI suggestions degraded, using defaults")
        return result.output.suggestions

    # On complete failure, return empty list
    return []
```

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement skills following TDD (write failing tests first)
3. Integrate skills with agent implementations
