"""
Base skill abstract class.

T014: BaseSkill abstract class with Generic[TInput, TOutput]
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from src.models.skill import SkillCategory
from src.services.skills.context import SkillContext
from src.services.skills.models import SkillMetadata, SkillResult

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class BaseSkill(ABC, Generic[TInput, TOutput]):
    """
    Abstract base class for all skills.

    T014: BaseSkill abstract class

    Skills must:
    1. Define input/output types via generics
    2. Implement the execute() method
    3. Provide metadata via get_metadata()

    Example:
        class TaskCreationSkill(BaseSkill[TaskCreateInput, TaskCreateOutput]):
            def get_metadata(self) -> SkillMetadata:
                return SkillMetadata(
                    name="task_creation",
                    description="Create a new task",
                    category=SkillCategory.TASK_MANAGEMENT,
                )

            async def execute(
                self, input: TaskCreateInput, context: SkillContext
            ) -> SkillResult[TaskCreateOutput]:
                # Implementation here
                ...
    """

    @abstractmethod
    def get_metadata(self) -> SkillMetadata:
        """
        Return metadata describing this skill's contract.

        This should be a static description - same every time.
        """
        ...

    @abstractmethod
    async def execute(self, input: TInput, context: SkillContext) -> SkillResult[TOutput]:
        """
        Execute the skill with the given input and context.

        Args:
            input: Validated input matching the skill's input schema
            context: Execution context with user info, correlation ID, etc.

        Returns:
            SkillResult with either data (success) or error (failure)
        """
        ...

    @property
    def name(self) -> str:
        """Convenience property to get skill name."""
        return self.get_metadata().name

    @property
    def category(self) -> SkillCategory:
        """Convenience property to get skill category."""
        return self.get_metadata().category

    def get_input_schema(self) -> dict[str, Any]:
        """Get JSON Schema for input validation."""
        return self.get_metadata().input_schema

    def get_output_schema(self) -> dict[str, Any]:
        """Get JSON Schema for output validation."""
        return self.get_metadata().output_schema

    def __repr__(self) -> str:
        meta = self.get_metadata()
        return f"<{self.__class__.__name__} name={meta.name} category={meta.category.value}>"
