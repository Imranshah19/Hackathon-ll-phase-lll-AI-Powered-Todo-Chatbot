"""
Skills Library for Todo Full-Stack Web Application.

T017: Skills package exports

This package provides:
- BaseSkill: Abstract base class for implementing skills
- SkillContext: Execution context with correlation ID, user info, etc.
- SkillMetadata: Skill contract metadata
- SkillResult: Generic result container for skill execution
- SkillRegistry: Discovery and lookup of registered skills
- @skill: Decorator to register skill classes

Usage:
    from src.services.skills import (
        BaseSkill,
        SkillContext,
        SkillMetadata,
        SkillResult,
        skill,
        get_registry,
    )

    @skill
    class MySkill(BaseSkill[MyInput, MyOutput]):
        def get_metadata(self) -> SkillMetadata:
            return SkillMetadata(
                name="my_skill",
                description="Does something useful",
                category=SkillCategory.TASK_MANAGEMENT,
            )

        async def execute(
            self, input: MyInput, context: SkillContext
        ) -> SkillResult[MyOutput]:
            # Implementation
            ...
"""

from src.services.skills.base import BaseSkill
from src.services.skills.context import SkillContext
from src.services.skills.models import SkillMetadata, SkillResult
from src.services.skills.registry import (
    SkillRegistry,
    get_registry,
    skill,
    skill_for_agents,
)

__all__ = [
    # Base class
    "BaseSkill",
    # Models
    "SkillContext",
    "SkillMetadata",
    "SkillResult",
    # Registry
    "SkillRegistry",
    "get_registry",
    "skill",
    "skill_for_agents",
]
