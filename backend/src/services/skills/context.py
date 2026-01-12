"""
Skill execution context.

T010: SkillContext model
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SkillContext(BaseModel):
    """
    Context passed to every skill execution.

    Contains metadata about the request, user, and execution environment.
    """

    correlation_id: UUID = Field(default_factory=uuid4)
    """Unique ID for tracing this request across services"""

    user_id: UUID | None = None
    """Authenticated user ID (None for unauthenticated operations)"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    """When execution started"""

    timeout_seconds: float = 30.0
    """Maximum execution time allowed"""

    metadata: dict[str, Any] = Field(default_factory=dict)
    """Additional context-specific data"""

    source_agent: str | None = None
    """Agent that invoked this skill"""

    parent_correlation_id: UUID | None = None
    """For nested/chained skill invocations"""

    @classmethod
    def create(
        cls,
        user_id: UUID | None = None,
        source_agent: str | None = None,
        timeout_seconds: float = 30.0,
        **metadata: Any,
    ) -> "SkillContext":
        """Factory method to create a new context."""
        return cls(
            user_id=user_id,
            source_agent=source_agent,
            timeout_seconds=timeout_seconds,
            metadata=metadata,
        )

    def child_context(self) -> "SkillContext":
        """Create a child context for nested skill invocations."""
        return SkillContext(
            user_id=self.user_id,
            source_agent=self.source_agent,
            timeout_seconds=self.timeout_seconds,
            metadata=self.metadata.copy(),
            parent_correlation_id=self.correlation_id,
        )
