"""
Skill registration and discovery.

T015: @skill decorator for registration
T016: SkillRegistry class
"""

from collections.abc import Callable
from typing import Any, TypeVar

from src.models.skill import SkillCategory
from src.services.skills.base import BaseSkill
from src.services.skills.models import SkillMetadata

T = TypeVar("T", bound=BaseSkill[Any, Any])


class SkillRegistry:
    """
    Registry for skill discovery and lookup.

    T016: SkillRegistry class

    Provides:
    - Registration of skill classes
    - Lookup by name
    - Lookup by category
    - Lookup by agent
    """

    _instance: "SkillRegistry | None" = None
    _skills: dict[str, type[BaseSkill[Any, Any]]]
    _instances: dict[str, BaseSkill[Any, Any]]

    def __new__(cls) -> "SkillRegistry":
        """Singleton pattern for global registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._skills = {}
            cls._instance._instances = {}
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the registry (useful for testing)."""
        cls._instance = None

    def register(self, skill_class: type[T]) -> type[T]:
        """
        Register a skill class with the registry.

        Args:
            skill_class: The skill class to register

        Returns:
            The same skill class (for decorator chaining)

        Raises:
            ValueError: If a skill with the same name is already registered
        """
        # Create an instance to get metadata
        instance = skill_class()
        metadata = instance.get_metadata()

        if metadata.name in self._skills:
            raise ValueError(
                f"Skill '{metadata.name}' is already registered. "
                f"Existing: {self._skills[metadata.name].__name__}, "
                f"New: {skill_class.__name__}"
            )

        self._skills[metadata.name] = skill_class
        self._instances[metadata.name] = instance
        return skill_class

    def get(self, name: str) -> BaseSkill[Any, Any] | None:
        """
        Get a skill instance by name.

        Args:
            name: The skill name (e.g., "task_creation")

        Returns:
            The skill instance, or None if not found
        """
        return self._instances.get(name)

    def get_class(self, name: str) -> type[BaseSkill[Any, Any]] | None:
        """
        Get a skill class by name.

        Args:
            name: The skill name

        Returns:
            The skill class, or None if not found
        """
        return self._skills.get(name)

    def get_all(self) -> list[BaseSkill[Any, Any]]:
        """Get all registered skill instances."""
        return list(self._instances.values())

    def get_by_category(self, category: SkillCategory) -> list[BaseSkill[Any, Any]]:
        """
        Get all skills in a category.

        Args:
            category: The skill category

        Returns:
            List of skill instances in that category
        """
        return [skill for skill in self._instances.values() if skill.category == category]

    def get_for_agent(self, agent: str) -> list[BaseSkill[Any, Any]]:
        """
        Get all skills available to a specific agent.

        Args:
            agent: The agent name (e.g., "TaskAgent")

        Returns:
            List of skill instances the agent can invoke
        """
        return [skill for skill in self._instances.values() if agent in skill.get_metadata().agents]

    def get_metadata(self, name: str) -> SkillMetadata | None:
        """
        Get metadata for a skill by name.

        Args:
            name: The skill name

        Returns:
            The skill metadata, or None if not found
        """
        skill = self._instances.get(name)
        return skill.get_metadata() if skill else None

    def list_names(self) -> list[str]:
        """Get all registered skill names."""
        return list(self._skills.keys())

    def list_categories(self) -> list[SkillCategory]:
        """Get all categories that have registered skills."""
        return list({skill.category for skill in self._instances.values()})

    def __contains__(self, name: str) -> bool:
        """Check if a skill is registered."""
        return name in self._skills

    def __len__(self) -> int:
        """Get the number of registered skills."""
        return len(self._skills)


# Global registry instance
_registry = SkillRegistry()


def get_registry() -> SkillRegistry:
    """Get the global skill registry."""
    return _registry


def skill(cls: type[T]) -> type[T]:
    """
    Decorator to register a skill class.

    T015: @skill decorator

    Usage:
        @skill
        class TaskCreationSkill(BaseSkill[TaskCreateInput, TaskCreateOutput]):
            ...
    """
    return _registry.register(cls)


def skill_for_agents(*agents: str) -> Callable[[type[T]], type[T]]:
    """
    Decorator factory to register a skill and assign it to specific agents.

    Usage:
        @skill_for_agents("TaskAgent", "OrchestratorAgent")
        class TaskCreationSkill(BaseSkill[TaskCreateInput, TaskCreateOutput]):
            ...
    """

    def decorator(cls: type[T]) -> type[T]:
        # First register the skill
        registered_cls = _registry.register(cls)

        # Then update its metadata with agent assignments
        instance = _registry.get(registered_cls().get_metadata().name)
        if instance:
            metadata = instance.get_metadata()
            metadata.agents = list(agents)

        return registered_cls

    return decorator
