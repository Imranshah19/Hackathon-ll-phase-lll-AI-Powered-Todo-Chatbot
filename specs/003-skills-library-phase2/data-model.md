# Data Model: Skills Library Phase-2

**Date**: 2026-01-12
**Branch**: `003-skills-library-phase2`
**Source**: [spec.md](./spec.md), [research.md](./research.md)

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SKILL LIBRARY                                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│     Skill       │      │ SkillInvocation │      │   SkillResult   │
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ name (PK)       │◄────▶│ id (PK)         │──────│ invocation_id   │
│ description     │      │ skill_name (FK) │      │ success         │
│ category        │      │ input_payload   │      │ output_payload  │
│ assigned_to[]   │      │ invoking_agent  │      │ failure_code    │
│ input_schema    │      │ correlation_id  │      │ failure_message │
│ output_schema   │      │ timestamp       │      │ duration_ms     │
│ success_criteria│      │ status          │      │ timestamp       │
│ failure_modes[] │      └─────────────────┘      └─────────────────┘
│ timeout_seconds │
└─────────────────┘
         │
         │ defines
         ▼
┌─────────────────┐
│   FailureMode   │
├─────────────────┤
│ code (PK)       │
│ message_template│
│ severity        │
│ suggested_action│
└─────────────────┘
```

---

## Core Entities

### 1. Skill

The fundamental unit of capability in the skills library.

```python
from pydantic import BaseModel, Field
from typing import Any
from enum import Enum

class SkillCategory(str, Enum):
    """Skill category enumeration."""
    ORCHESTRATION = "orchestration"
    AUTHENTICATION = "authentication"
    TASK_MANAGEMENT = "task_management"
    USER_MANAGEMENT = "user_management"
    AI = "ai"
    PLANNING = "planning"
    EXECUTION = "execution"

class SkillDefinition(BaseModel):
    """
    Metadata definition for a skill.
    Note: This is for documentation/discovery. Actual skill implementation
    is in code via BaseSkill subclasses.
    """
    name: str = Field(
        ...,
        pattern=r'^[a-z][a-z0-9_]*$',
        max_length=64,
        description="Unique identifier (snake_case)"
    )
    description: str = Field(
        ...,
        max_length=500,
        description="Human-readable description of what the skill does"
    )
    category: SkillCategory = Field(
        ...,
        description="Logical grouping for organization"
    )
    assigned_to: list[str] = Field(
        default_factory=list,
        description="List of agent names that use this skill"
    )
    input_schema: dict[str, Any] = Field(
        ...,
        description="JSON Schema for input validation"
    )
    output_schema: dict[str, Any] = Field(
        ...,
        description="JSON Schema for output structure"
    )
    success_criteria: list[str] = Field(
        default_factory=list,
        description="Measurable conditions for success"
    )
    failure_modes: list[str] = Field(
        default_factory=list,
        description="List of FailureCode values this skill can return"
    )
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Maximum execution time before timeout"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "task_creation",
                "description": "Create a new task for a user",
                "category": "task_management",
                "assigned_to": ["TaskAgent"],
                "input_schema": {"type": "object", "properties": {...}},
                "output_schema": {"type": "object", "properties": {...}},
                "success_criteria": ["Task is persisted with unique ID"],
                "failure_modes": ["VALIDATION_ERROR", "PERSISTENCE_ERROR"],
                "timeout_seconds": 30
            }
        }
```

**Validation Rules:**
- `name` must be unique across all skills (globally)
- `name` must be snake_case format
- `assigned_to` must reference valid agent names
- `failure_modes` must reference valid FailureCode values

---

### 2. SkillInvocation

Represents a single execution request of a skill.

```python
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Any
from enum import Enum

class InvocationStatus(str, Enum):
    """Status of a skill invocation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class SkillInvocation(BaseModel):
    """
    Record of a skill invocation request.
    Created when skill execution begins.
    """
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique invocation identifier"
    )
    skill_name: str = Field(
        ...,
        description="Name of the skill being invoked"
    )
    input_payload: dict[str, Any] = Field(
        ...,
        description="Input data passed to the skill"
    )
    invoking_agent: str = Field(
        ...,
        description="Name of the agent that invoked this skill"
    )
    correlation_id: UUID = Field(
        ...,
        description="ID for tracing across multiple skills"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the invocation was created"
    )
    status: InvocationStatus = Field(
        default=InvocationStatus.PENDING,
        description="Current status of the invocation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "skill_name": "task_creation",
                "input_payload": {"title": "Buy groceries", "user_id": "..."},
                "invoking_agent": "TaskAgent",
                "correlation_id": "550e8400-e29b-41d4-a716-446655440001",
                "timestamp": "2026-01-12T10:00:00Z",
                "status": "pending"
            }
        }
```

**State Transitions:**
```
PENDING ──▶ RUNNING ──▶ COMPLETED
                   └──▶ FAILED
                   └──▶ TIMEOUT
```

---

### 3. SkillResult

The outcome of a skill execution.

```python
from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import datetime
from typing import Any, Self

class SkillResult(BaseModel):
    """
    Result of a skill execution.
    Either output (success) or failure_code/message (failure) is populated.
    """
    invocation_id: UUID = Field(
        ...,
        description="Reference to the SkillInvocation"
    )
    success: bool = Field(
        ...,
        description="Whether the skill executed successfully"
    )
    output_payload: dict[str, Any] | None = Field(
        default=None,
        description="Output data on success"
    )
    failure_code: str | None = Field(
        default=None,
        description="FailureCode value on failure"
    )
    failure_message: str | None = Field(
        default=None,
        description="Human-readable error message on failure"
    )
    failure_details: dict[str, Any] | None = Field(
        default=None,
        description="Additional error context (sanitized)"
    )
    duration_ms: int = Field(
        ...,
        ge=0,
        description="Execution duration in milliseconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the result was produced"
    )

    @model_validator(mode='after')
    def validate_success_failure(self) -> Self:
        """Ensure success has output, failure has code/message."""
        if self.success:
            if self.output_payload is None:
                raise ValueError("Successful result must have output_payload")
            if self.failure_code is not None:
                raise ValueError("Successful result cannot have failure_code")
        else:
            if self.failure_code is None:
                raise ValueError("Failed result must have failure_code")
            if self.failure_message is None:
                raise ValueError("Failed result must have failure_message")
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "invocation_id": "550e8400-e29b-41d4-a716-446655440000",
                "success": True,
                "output_payload": {"task_id": "...", "title": "Buy groceries"},
                "failure_code": None,
                "failure_message": None,
                "duration_ms": 45,
                "timestamp": "2026-01-12T10:00:00.045Z"
            }
        }
```

---

### 4. FailureMode

Definition of a possible failure outcome.

```python
from pydantic import BaseModel, Field
from enum import Enum

class FailureCode(str, Enum):
    """
    Standard failure codes used across all skills.
    Based on spec.md Failure Mode Taxonomy.
    """
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    RATE_EXCEEDED = "RATE_EXCEEDED"
    TIMEOUT = "TIMEOUT"
    PERSISTENCE_ERROR = "PERSISTENCE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class Severity(str, Enum):
    """Severity level determining recoverability."""
    RECOVERABLE = "recoverable"
    FATAL = "fatal"

class FailureMode(BaseModel):
    """
    Definition of a failure mode.
    Static configuration, not persisted per-invocation.
    """
    code: FailureCode = Field(
        ...,
        description="Unique error identifier"
    )
    message_template: str = Field(
        ...,
        max_length=200,
        description="Template for human-readable message"
    )
    severity: Severity = Field(
        ...,
        description="Whether operation can be retried"
    )
    suggested_action: str = Field(
        ...,
        max_length=200,
        description="Guidance for handling this failure"
    )

# Standard failure modes (static configuration)
STANDARD_FAILURE_MODES: dict[FailureCode, FailureMode] = {
    FailureCode.VALIDATION_ERROR: FailureMode(
        code=FailureCode.VALIDATION_ERROR,
        message_template="Input validation failed: {details}",
        severity=Severity.RECOVERABLE,
        suggested_action="Fix input and retry"
    ),
    FailureCode.NOT_FOUND: FailureMode(
        code=FailureCode.NOT_FOUND,
        message_template="Resource not found: {resource}",
        severity=Severity.RECOVERABLE,
        suggested_action="Verify resource exists before operation"
    ),
    FailureCode.UNAUTHORIZED: FailureMode(
        code=FailureCode.UNAUTHORIZED,
        message_template="Access denied: {reason}",
        severity=Severity.FATAL,
        suggested_action="Check permissions or re-authenticate"
    ),
    FailureCode.RATE_EXCEEDED: FailureMode(
        code=FailureCode.RATE_EXCEEDED,
        message_template="Rate limit exceeded. Retry after {retry_after}s",
        severity=Severity.RECOVERABLE,
        suggested_action="Wait and retry with backoff"
    ),
    FailureCode.TIMEOUT: FailureMode(
        code=FailureCode.TIMEOUT,
        message_template="Operation timed out after {timeout}s",
        severity=Severity.RECOVERABLE,
        suggested_action="Retry or increase timeout"
    ),
    FailureCode.PERSISTENCE_ERROR: FailureMode(
        code=FailureCode.PERSISTENCE_ERROR,
        message_template="Database operation failed",
        severity=Severity.RECOVERABLE,
        suggested_action="Retry operation"
    ),
    FailureCode.EXTERNAL_SERVICE_ERROR: FailureMode(
        code=FailureCode.EXTERNAL_SERVICE_ERROR,
        message_template="External service unavailable",
        severity=Severity.RECOVERABLE,
        suggested_action="Service degradation active; retry later"
    ),
    FailureCode.INTERNAL_ERROR: FailureMode(
        code=FailureCode.INTERNAL_ERROR,
        message_template="An unexpected error occurred",
        severity=Severity.FATAL,
        suggested_action="Contact support with correlation ID"
    ),
}
```

---

## Skill-Specific Input/Output Schemas

### Category: Task Management

#### task_creation

```python
class TaskCreateInput(BaseModel):
    """Input for task_creation skill."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    priority: int = Field(1, ge=1, le=5)
    due_date: datetime | None = None
    user_id: UUID

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

class TaskCreateOutput(BaseModel):
    """Output for task_creation skill."""
    task_id: UUID
    title: str
    created_at: datetime
```

#### task_retrieval

```python
class TaskRetrievalInput(BaseModel):
    """Input for task_retrieval skill."""
    user_id: UUID
    task_id: UUID | None = None  # If None, retrieve all for user
    status_filter: str | None = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

class TaskItem(BaseModel):
    """Single task in retrieval output."""
    task_id: UUID
    title: str
    description: str | None
    status: str
    priority: int
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime

class TaskRetrievalOutput(BaseModel):
    """Output for task_retrieval skill."""
    tasks: list[TaskItem]
    total_count: int
    has_more: bool
```

#### task_update

```python
class TaskUpdateInput(BaseModel):
    """Input for task_update skill."""
    task_id: UUID
    user_id: UUID  # For ownership validation
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    status: str | None = None
    priority: int | None = Field(None, ge=1, le=5)
    due_date: datetime | None = None

class TaskUpdateOutput(BaseModel):
    """Output for task_update skill."""
    task_id: UUID
    updated_fields: list[str]
    updated_at: datetime
```

#### task_deletion

```python
class TaskDeletionInput(BaseModel):
    """Input for task_deletion skill."""
    task_id: UUID
    user_id: UUID  # For ownership validation

class TaskDeletionOutput(BaseModel):
    """Output for task_deletion skill."""
    task_id: UUID
    deleted_at: datetime
```

---

### Category: Authentication

#### token_generation

```python
class TokenGenerationInput(BaseModel):
    """Input for token_generation skill."""
    user_id: UUID
    email: str
    scopes: list[str] = Field(default_factory=list)
    expires_in_seconds: int = Field(3600, ge=300, le=86400)

class TokenGenerationOutput(BaseModel):
    """Output for token_generation skill."""
    access_token: str
    token_type: str = "Bearer"
    expires_at: datetime
```

#### token_validation

```python
class TokenValidationInput(BaseModel):
    """Input for token_validation skill."""
    token: str
    required_scopes: list[str] = Field(default_factory=list)

class TokenValidationOutput(BaseModel):
    """Output for token_validation skill."""
    valid: bool
    user_id: UUID | None
    email: str | None
    scopes: list[str]
    expires_at: datetime | None
```

---

### Category: User Management

#### user_creation

```python
class UserCreationInput(BaseModel):
    """Input for user_creation skill."""
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    display_name: str | None = Field(None, max_length=100)

class UserCreationOutput(BaseModel):
    """Output for user_creation skill."""
    user_id: UUID
    email: str
    created_at: datetime
```

#### ownership_validation

```python
class OwnershipValidationInput(BaseModel):
    """Input for ownership_validation skill."""
    user_id: UUID
    resource_type: str  # e.g., "task"
    resource_id: UUID

class OwnershipValidationOutput(BaseModel):
    """Output for ownership_validation skill."""
    is_owner: bool
    resource_type: str
    resource_id: UUID
```

---

### Category: AI

#### suggestion_generation

```python
class SuggestionGenerationInput(BaseModel):
    """Input for suggestion_generation skill."""
    user_id: UUID
    context: str | None = None  # Optional context for suggestions
    count: int = Field(3, ge=1, le=10)

class TaskSuggestion(BaseModel):
    """Single suggestion in output."""
    title: str
    description: str | None
    priority: int
    confidence: float = Field(..., ge=0.0, le=1.0)

class SuggestionGenerationOutput(BaseModel):
    """Output for suggestion_generation skill."""
    suggestions: list[TaskSuggestion]
    degraded: bool = False  # True if AI service unavailable
```

---

## Database Schema (PostgreSQL)

Skills library entities are primarily in-memory (skill definitions) with optional observability persistence.

```sql
-- Optional: Skill invocation logging for observability (P2)
-- Only created if observability feature is enabled

CREATE TABLE IF NOT EXISTS skill_invocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name VARCHAR(64) NOT NULL,
    invoking_agent VARCHAR(64) NOT NULL,
    correlation_id UUID NOT NULL,
    input_payload JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Indexes for querying
    INDEX idx_skill_invocations_skill_name (skill_name),
    INDEX idx_skill_invocations_correlation_id (correlation_id),
    INDEX idx_skill_invocations_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS skill_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invocation_id UUID NOT NULL REFERENCES skill_invocations(id),
    success BOOLEAN NOT NULL,
    output_payload JSONB,
    failure_code VARCHAR(50),
    failure_message TEXT,
    failure_details JSONB,
    duration_ms INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Ensure one result per invocation
    CONSTRAINT unique_invocation_result UNIQUE (invocation_id),

    -- Index for metrics queries
    INDEX idx_skill_results_success (success),
    INDEX idx_skill_results_failure_code (failure_code)
);
```

---

## Validation Rules Summary

| Entity | Field | Validation |
|--------|-------|------------|
| Skill | name | Unique, snake_case, 1-64 chars |
| Skill | category | Must be valid SkillCategory enum |
| Skill | timeout_seconds | 1-300 |
| SkillInvocation | skill_name | Must exist in registry |
| SkillInvocation | correlation_id | Valid UUID |
| SkillResult | success=true | Must have output_payload |
| SkillResult | success=false | Must have failure_code and failure_message |
| SkillResult | duration_ms | >= 0 |
| TaskCreateInput | title | 1-200 chars, not whitespace |
| TaskCreateInput | priority | 1-5 |
| UserCreationInput | email | Valid email format |
| UserCreationInput | password | Min 8 chars |

---

## State Transitions

### SkillInvocation Status

```
┌─────────┐     execute()     ┌─────────┐
│ PENDING │─────────────────▶│ RUNNING │
└─────────┘                   └────┬────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
              ┌───────────┐ ┌──────────┐ ┌─────────┐
              │ COMPLETED │ │  FAILED  │ │ TIMEOUT │
              └───────────┘ └──────────┘ └─────────┘
```

**Transition Rules:**
- PENDING → RUNNING: When skill execution begins
- RUNNING → COMPLETED: When skill returns success
- RUNNING → FAILED: When skill returns failure or throws exception
- RUNNING → TIMEOUT: When execution exceeds timeout_seconds
