# Research: Skills Library Phase-2

**Date**: 2026-01-12
**Branch**: `003-skills-library-phase2`
**Status**: Complete

---

## Research Questions Addressed

1. How to implement typed skill schemas with Pydantic
2. How to design failure mode taxonomy and error handling
3. How to implement skill composition (chaining, parallel execution)
4. How to handle timeouts, retries, and graceful degradation

---

## 1. Skill Schema Design with Pydantic

### Decision
Use Pydantic `BaseModel` for all skill input/output schemas with a generic `BaseSkill` abstract class.

### Rationale
- Pydantic provides automatic validation, serialization, and OpenAPI schema generation
- Generic typing allows type-safe skill definitions
- Integrates seamlessly with FastAPI for automatic API documentation

### Implementation Pattern

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

# Generic type variables for input/output
TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)

class SkillMetadata(BaseModel):
    """Metadata attached to every skill result."""
    correlation_id: UUID
    duration_ms: int
    timestamp: datetime
    skill_name: str

class SkillResult(BaseModel, Generic[TOutput]):
    """Standard result wrapper for all skills."""
    success: bool
    output: TOutput | None = None
    failure: "FailureResponse | None" = None
    metadata: SkillMetadata

class BaseSkill(ABC, Generic[TInput, TOutput]):
    """Abstract base class for all skills."""

    name: str  # Unique identifier
    description: str  # Human-readable purpose
    category: str  # Logical grouping

    @abstractmethod
    def execute(self, input: TInput, context: "SkillContext") -> SkillResult[TOutput]:
        """Execute the skill with validated input."""
        pass

    @classmethod
    def input_schema(cls) -> type[TInput]:
        """Return the Pydantic model for input validation."""
        pass

    @classmethod
    def output_schema(cls) -> type[TOutput]:
        """Return the Pydantic model for output."""
        pass
```

### Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| dataclasses | No automatic validation, no OpenAPI generation |
| TypedDict | No runtime validation, less IDE support |
| attrs | Less ecosystem integration with FastAPI |

---

## 2. Skill Registry Pattern

### Decision
Implement auto-discovery registry using Python decorators and module inspection.

### Rationale
- Decorators provide clean registration syntax
- Module inspection enables automatic discovery at startup
- Centralized registry enables runtime skill lookup by agents

### Implementation Pattern

```python
from typing import Dict, Type
from functools import wraps

class SkillRegistry:
    """Central registry for skill discovery."""

    _skills: Dict[str, Type[BaseSkill]] = {}
    _by_category: Dict[str, list[str]] = {}
    _by_agent: Dict[str, list[str]] = {}

    @classmethod
    def register(cls, skill_class: Type[BaseSkill]) -> Type[BaseSkill]:
        """Register a skill class."""
        name = skill_class.name
        cls._skills[name] = skill_class

        # Index by category
        category = skill_class.category
        if category not in cls._by_category:
            cls._by_category[category] = []
        cls._by_category[category].append(name)

        # Index by assigned agents
        for agent in getattr(skill_class, 'assigned_to', []):
            if agent not in cls._by_agent:
                cls._by_agent[agent] = []
            cls._by_agent[agent].append(name)

        return skill_class

    @classmethod
    def get(cls, name: str) -> Type[BaseSkill] | None:
        """Get a skill by name."""
        return cls._skills.get(name)

    @classmethod
    def get_for_agent(cls, agent_name: str) -> list[str]:
        """Get all skills assigned to an agent."""
        return cls._by_agent.get(agent_name, [])

# Decorator for registration
def skill(cls: Type[BaseSkill]) -> Type[BaseSkill]:
    """Decorator to register a skill."""
    return SkillRegistry.register(cls)
```

### Usage Example

```python
@skill
class TaskCreationSkill(BaseSkill[TaskCreateInput, TaskCreateOutput]):
    name = "task_creation"
    description = "Create a new task for a user"
    category = "task_management"
    assigned_to = ["TaskAgent"]

    def execute(self, input: TaskCreateInput, context: SkillContext) -> SkillResult[TaskCreateOutput]:
        # Implementation
        pass
```

---

## 3. Failure Mode Taxonomy

### Decision
Use enum-based failure codes with structured `FailureResponse` model containing severity and recoverability.

### Rationale
- Enums prevent typos and enable IDE autocomplete
- Structured responses enable consistent error handling
- Severity levels enable appropriate agent response strategies

### Implementation Pattern

```python
from enum import Enum
from pydantic import BaseModel
from typing import Any

class FailureCode(str, Enum):
    """Standard failure codes across all skills."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    RATE_EXCEEDED = "RATE_EXCEEDED"
    TIMEOUT = "TIMEOUT"
    PERSISTENCE_ERROR = "PERSISTENCE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class Severity(str, Enum):
    """Failure severity levels."""
    RECOVERABLE = "recoverable"  # Can retry or handle gracefully
    FATAL = "fatal"  # Cannot recover, must abort

# Mapping of codes to default severity
FAILURE_SEVERITY: dict[FailureCode, Severity] = {
    FailureCode.VALIDATION_ERROR: Severity.RECOVERABLE,
    FailureCode.NOT_FOUND: Severity.RECOVERABLE,
    FailureCode.UNAUTHORIZED: Severity.FATAL,
    FailureCode.RATE_EXCEEDED: Severity.RECOVERABLE,
    FailureCode.TIMEOUT: Severity.RECOVERABLE,
    FailureCode.PERSISTENCE_ERROR: Severity.RECOVERABLE,
    FailureCode.EXTERNAL_SERVICE_ERROR: Severity.RECOVERABLE,
    FailureCode.INTERNAL_ERROR: Severity.FATAL,
}

class FailureResponse(BaseModel):
    """Structured failure response."""
    code: FailureCode
    message: str  # Human-readable, safe for display
    details: dict[str, Any] = {}  # Context-specific, sanitized
    correlation_id: UUID
    timestamp: datetime
    recoverable: bool

    @classmethod
    def from_code(
        cls,
        code: FailureCode,
        message: str,
        correlation_id: UUID,
        details: dict[str, Any] | None = None
    ) -> "FailureResponse":
        """Create failure response with auto-computed severity."""
        return cls(
            code=code,
            message=message,
            details=details or {},
            correlation_id=correlation_id,
            timestamp=datetime.utcnow(),
            recoverable=FAILURE_SEVERITY[code] == Severity.RECOVERABLE
        )
```

### Error Wrapping Pattern

```python
def wrap_unexpected_error(
    error: Exception,
    correlation_id: UUID
) -> FailureResponse:
    """Wrap unexpected errors without exposing internals."""
    # Log full error internally with correlation_id
    logger.error(f"[{correlation_id}] Unexpected error: {error}", exc_info=True)

    # Return sanitized response
    return FailureResponse.from_code(
        code=FailureCode.INTERNAL_ERROR,
        message="An unexpected error occurred. Please try again.",
        correlation_id=correlation_id,
        details={"support_reference": str(correlation_id)}
    )
```

---

## 4. Skill Composition Patterns

### Decision
Implement `SkillChain` for sequential composition and `SkillParallel` for concurrent execution with fail-fast semantics.

### Rationale
- Clear separation between sequential and parallel execution
- Fail-fast prevents wasted work on doomed chains
- Type-safe data flow between composed skills

### Implementation Pattern

```python
from typing import Callable, Any

class SkillChain:
    """Sequential skill composition with data transformation."""

    def __init__(self):
        self._steps: list[tuple[BaseSkill, Callable[[Any], Any]]] = []

    def then(
        self,
        skill: BaseSkill,
        transform: Callable[[Any], Any] | None = None
    ) -> "SkillChain":
        """Add a skill to the chain with optional output transformation."""
        self._steps.append((skill, transform or (lambda x: x)))
        return self

    def execute(self, initial_input: Any, context: SkillContext) -> SkillResult:
        """Execute chain, stopping on first failure."""
        current_input = initial_input

        for skill, transform in self._steps:
            result = skill.execute(current_input, context)

            if not result.success:
                # Fail-fast: return failure with chain context
                return SkillResult(
                    success=False,
                    failure=result.failure,
                    metadata=result.metadata
                )

            # Transform output for next skill's input
            current_input = transform(result.output)

        return result

class SkillParallel:
    """Parallel skill execution for independent operations."""

    def __init__(self, skills: list[tuple[BaseSkill, Any]]):
        self._skills = skills  # List of (skill, input) pairs

    async def execute(self, context: SkillContext) -> list[SkillResult]:
        """Execute all skills concurrently."""
        import asyncio

        async def run_skill(skill: BaseSkill, input: Any) -> SkillResult:
            # Run in thread pool for sync skills
            return await asyncio.to_thread(skill.execute, input, context)

        tasks = [run_skill(s, i) for s, i in self._skills]
        return await asyncio.gather(*tasks)
```

### Usage Example

```python
# Chain: validate user -> create task -> return task
chain = (
    SkillChain()
    .then(ownership_validation_skill)
    .then(task_creation_skill, lambda user: TaskCreateInput(user_id=user.id, ...))
)

result = chain.execute(user_input, context)
```

---

## 5. Timeout and Retry Patterns

### Decision
Use `tenacity` library for retries with exponential backoff, and `asyncio.timeout` for timeouts.

### Rationale
- `tenacity` is battle-tested with flexible retry strategies
- Built-in support for exponential backoff and jitter
- Can specify retry conditions (e.g., only on certain failure codes)

### Implementation Pattern

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import asyncio
from contextlib import asynccontextmanager

class SkillExecutor:
    """Executes skills with timeout and retry policies."""

    DEFAULT_TIMEOUT_SECONDS = 30

    @asynccontextmanager
    async def with_timeout(self, timeout_seconds: float | None = None):
        """Context manager for skill timeout."""
        timeout = timeout_seconds or self.DEFAULT_TIMEOUT_SECONDS
        try:
            async with asyncio.timeout(timeout):
                yield
        except asyncio.TimeoutError:
            raise SkillTimeoutError(f"Skill execution exceeded {timeout}s timeout")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(RetryableSkillError)
    )
    async def execute_with_retry(
        self,
        skill: BaseSkill,
        input: Any,
        context: SkillContext
    ) -> SkillResult:
        """Execute skill with retry on recoverable errors."""
        result = await asyncio.to_thread(skill.execute, input, context)

        if not result.success and result.failure.recoverable:
            raise RetryableSkillError(result.failure)

        return result
```

### Graceful Degradation Pattern

```python
class AISkillBase(BaseSkill):
    """Base class for AI skills with built-in graceful degradation."""

    async def execute_with_fallback(
        self,
        input: Any,
        context: SkillContext
    ) -> SkillResult:
        """Execute AI skill with fallback on failure."""
        try:
            async with SkillExecutor().with_timeout(60):  # AI gets longer timeout
                return await self._call_ai_service(input, context)
        except (SkillTimeoutError, ExternalServiceError):
            # Return degraded response
            return self._fallback_response(input, context)

    def _fallback_response(self, input: Any, context: SkillContext) -> SkillResult:
        """Provide degraded but functional response."""
        return SkillResult(
            success=True,
            output=self._default_output(),
            metadata=SkillMetadata(
                correlation_id=context.correlation_id,
                duration_ms=0,
                timestamp=datetime.utcnow(),
                skill_name=self.name,
                degraded=True  # Flag for observability
            )
        )
```

---

## 6. Input Validation Strategy

### Decision
Use Pydantic validators with custom error messages, validated at executor boundary before skill execution.

### Rationale
- Single validation point prevents duplicate checks
- Custom validators provide domain-specific rules
- Clear error messages identify exact validation failures

### Implementation Pattern

```python
from pydantic import BaseModel, field_validator, ValidationError

class TaskCreateInput(BaseModel):
    """Input schema for task creation with validation."""
    title: str
    description: str | None = None
    priority: int = 1
    user_id: UUID

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        return v.strip()

    @field_validator('priority')
    @classmethod
    def priority_in_range(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError('Priority must be between 1 and 5')
        return v

def validate_skill_input(
    skill: BaseSkill,
    raw_input: dict,
    correlation_id: UUID
) -> tuple[Any | None, FailureResponse | None]:
    """Validate input and return typed model or failure."""
    try:
        input_model = skill.input_schema()(**raw_input)
        return input_model, None
    except ValidationError as e:
        # Format validation errors for user
        errors = [
            f"{err['loc'][0]}: {err['msg']}"
            for err in e.errors()
        ]
        return None, FailureResponse.from_code(
            code=FailureCode.VALIDATION_ERROR,
            message="Input validation failed",
            correlation_id=correlation_id,
            details={"errors": errors}
        )
```

---

## 7. Observability Integration

### Decision
Use structured logging with correlation IDs, and emit metrics for duration and success/failure rates.

### Rationale
- Correlation IDs enable tracing across skill chains
- Structured logs enable querying and alerting
- Metrics enable performance monitoring and SLO tracking

### Implementation Pattern

```python
import structlog
from prometheus_client import Counter, Histogram

# Metrics
skill_invocations = Counter(
    'skill_invocations_total',
    'Total skill invocations',
    ['skill_name', 'status']
)
skill_duration = Histogram(
    'skill_duration_seconds',
    'Skill execution duration',
    ['skill_name']
)

logger = structlog.get_logger()

class ObservableSkillExecutor:
    """Skill executor with built-in observability."""

    def execute(
        self,
        skill: BaseSkill,
        input: Any,
        context: SkillContext
    ) -> SkillResult:
        start = time.perf_counter()
        log = logger.bind(
            skill_name=skill.name,
            correlation_id=str(context.correlation_id),
            agent=context.invoking_agent
        )

        log.info("skill_invocation_started")

        try:
            result = skill.execute(input, context)
            duration = time.perf_counter() - start

            status = "success" if result.success else "failure"
            skill_invocations.labels(skill_name=skill.name, status=status).inc()
            skill_duration.labels(skill_name=skill.name).observe(duration)

            log.info(
                "skill_invocation_completed",
                success=result.success,
                duration_ms=int(duration * 1000),
                failure_code=result.failure.code if result.failure else None
            )

            return result

        except Exception as e:
            duration = time.perf_counter() - start
            skill_invocations.labels(skill_name=skill.name, status="error").inc()

            log.error(
                "skill_invocation_error",
                error=str(e),
                duration_ms=int(duration * 1000)
            )
            raise
```

---

## Summary of Decisions

| Topic | Decision | Key Library/Pattern |
|-------|----------|---------------------|
| Schema Definition | Pydantic BaseModel with generics | `pydantic` |
| Skill Registration | Decorator-based auto-registry | `@skill` decorator |
| Failure Taxonomy | Enum codes with severity mapping | `FailureCode` enum |
| Skill Composition | Chain (sequential) / Parallel patterns | Custom classes |
| Timeouts/Retries | tenacity + asyncio.timeout | `tenacity` library |
| Validation | Pydantic validators at executor boundary | `field_validator` |
| Observability | structlog + prometheus metrics | `structlog`, `prometheus_client` |

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Async vs sync skills? | Phase-2 uses sync execution (run in thread pool for blocking ops) |
| Schema versioning? | Static schemas at deployment; versioning deferred to Phase-3 |
| Skill dependencies? | Handled via composition, not injection |
| Transaction handling? | Individual skills are atomic; cross-skill transactions via orchestration |
