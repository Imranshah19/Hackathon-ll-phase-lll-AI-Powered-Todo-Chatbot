"""
Skill models for metadata and results.

T011: SkillMetadata model
T013: SkillResult model
"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.failure_mode import FailureResponse
from src.models.skill import SkillCategory

TOutput = TypeVar("TOutput")


class SkillMetadata(BaseModel):
    """
    Metadata describing a skill's contract.

    T011: SkillMetadata model
    """

    name: str
    """Unique identifier (snake_case)"""

    description: str
    """What the skill does"""

    category: SkillCategory
    """Which category this skill belongs to"""

    version: str = "1.0.0"
    """Skill version for compatibility tracking"""

    input_schema: dict[str, Any] = Field(default_factory=dict)
    """JSON Schema for inputs"""

    output_schema: dict[str, Any] = Field(default_factory=dict)
    """JSON Schema for outputs"""

    success_criteria: list[str] = Field(default_factory=list)
    """Measurable success conditions"""

    failure_modes: list[str] = Field(default_factory=list)
    """Enumerated error codes this skill can return"""

    timeout_seconds: float = 30.0
    """Default timeout for this skill"""

    retryable: bool = False
    """Whether this skill can be safely retried on failure"""

    idempotent: bool = False
    """Whether repeated calls with same input produce same result"""

    agents: list[str] = Field(default_factory=list)
    """Agents that can invoke this skill"""


class SkillResult(BaseModel, Generic[TOutput]):
    """
    Generic result container for skill execution.

    T013: SkillResult model

    Either `data` (success) or `error` (failure) will be set, never both.
    """

    success: bool
    """Whether the skill executed successfully"""

    data: TOutput | None = None
    """Output data on success"""

    error: FailureResponse | None = None
    """Error details on failure"""

    correlation_id: UUID
    """Request correlation ID"""

    duration_ms: int
    """Execution time in milliseconds"""

    skill_name: str
    """Name of the skill that was executed"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    """When the result was produced"""

    metadata: dict[str, Any] = Field(default_factory=dict)
    """Additional result metadata"""

    @classmethod
    def ok(
        cls,
        data: TOutput,
        correlation_id: UUID,
        skill_name: str,
        duration_ms: int,
        **metadata: Any,
    ) -> "SkillResult[TOutput]":
        """Create a successful result."""
        return cls(
            success=True,
            data=data,
            error=None,
            correlation_id=correlation_id,
            duration_ms=duration_ms,
            skill_name=skill_name,
            metadata=metadata,
        )

    @classmethod
    def fail(
        cls,
        error: FailureResponse,
        correlation_id: UUID,
        skill_name: str,
        duration_ms: int,
        **metadata: Any,
    ) -> "SkillResult[TOutput]":
        """Create a failed result."""
        return cls(
            success=False,
            data=None,
            error=error,
            correlation_id=correlation_id,
            duration_ms=duration_ms,
            skill_name=skill_name,
            metadata=metadata,
        )
