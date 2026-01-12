"""
Skill models and enums.

T006: SkillCategory enum for the 7 skill categories defined in spec.md
"""

from enum import Enum


class SkillCategory(str, Enum):
    """
    Categories of skills in the skills library.

    Each category groups related skills that serve a common purpose.
    See: phase-2/skills.spec.md Section 1.2
    """

    ORCHESTRATION = "orchestration"
    """Request routing, workflow management (4 skills)"""

    AUTHENTICATION = "authentication"
    """Identity verification, sessions (5 skills)"""

    TASK_MANAGEMENT = "task_management"
    """Task CRUD with isolation (5 skills)"""

    USER_MANAGEMENT = "user_management"
    """Account lifecycle (4 skills)"""

    AI = "ai"
    """Intelligent suggestions (3 skills)"""

    PLANNING = "planning"
    """Goal decomposition (3 skills)"""

    EXECUTION = "execution"
    """Task execution and progress (3 skills)"""
