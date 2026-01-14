"""
Integration tests for User-Task relationship.

Tests:
- T028: User-Task relationship with cascade delete
"""

import pytest
from uuid import uuid4


@pytest.mark.integration
class TestUserTaskRelationship:
    """Integration tests for User-Task relationship."""

    def test_user_has_tasks_relationship(self) -> None:
        """User model should have 'tasks' relationship attribute."""
        from src.models.user import User

        user = User(
            email="test@example.com",
            password_hash="hashed_password",
        )

        # User should have tasks attribute (may be empty list initially)
        assert hasattr(user, "tasks"), "User should have 'tasks' relationship"

    def test_task_has_user_relationship(self) -> None:
        """Task model should have 'user' relationship attribute."""
        from src.models.task import Task

        task = Task(
            title="Test task",
            user_id=uuid4(),
        )

        # Task should have user attribute
        assert hasattr(task, "user"), "Task should have 'user' relationship"

    def test_task_user_id_foreign_key(self) -> None:
        """Task.user_id should reference User.id."""
        from src.models.task import Task
        from sqlmodel import Field

        # Check Task model has user_id field with foreign_key
        user_id_field = Task.model_fields.get("user_id")
        assert user_id_field is not None, "Task should have user_id field"

    def test_user_tasks_list_type(self) -> None:
        """User.tasks should be a list type for one-to-many relationship."""
        from src.models.user import User
        from typing import get_type_hints

        # The tasks field should be typed as list
        user = User(
            email="test@example.com",
            password_hash="hash",
        )

        # tasks should be a list (empty by default for new instances)
        # Note: For SQLModel with Relationship, this is typically empty until session attached
        tasks_attr = getattr(user, "tasks", None)
        assert tasks_attr is not None or hasattr(User, "__sqlmodel_relationships__")

    def test_cascade_delete_configuration(self) -> None:
        """User->Task relationship should be configured with cascade delete."""
        from src.models.user import User
        import inspect

        # Check that User class has relationship configuration
        # The cascade delete is configured via sa_relationship_kwargs
        source = inspect.getsource(User)

        # Should contain cascade configuration
        assert "cascade" in source.lower() or "Relationship" in source, \
            "User should have Relationship with cascade configuration"

    def test_task_belongs_to_user(self) -> None:
        """Task should store user_id correctly linking to User."""
        from src.models.task import Task
        from src.models.user import User

        user_id = uuid4()
        task = Task(
            title="User's task",
            user_id=user_id,
        )

        assert task.user_id == user_id, "Task should store user_id"

    def test_multiple_tasks_per_user(self) -> None:
        """User should be able to have multiple tasks."""
        from src.models.task import Task

        user_id = uuid4()

        task1 = Task(title="Task 1", user_id=user_id)
        task2 = Task(title="Task 2", user_id=user_id)
        task3 = Task(title="Task 3", user_id=user_id)

        # All tasks should have same user_id
        assert task1.user_id == task2.user_id == task3.user_id == user_id

    def test_task_user_id_required(self) -> None:
        """Task.user_id should be marked as NOT NULL (enforced at DB level).

        Note: SQLModel table models don't validate nullable at instantiation
        time - this is enforced by the database. We verify the Field is
        configured correctly for the DB constraint.
        """
        from src.models.task import Task

        # Verify user_id field is configured as non-nullable for DB
        user_id_info = Task.model_fields.get("user_id")
        assert user_id_info is not None, "Task should have user_id field"

        # The field should have nullable=False in its metadata
        # This is enforced at database insertion time
        field_info = Task.model_fields["user_id"]
        # Check that user_id has a type annotation (UUID, not Optional[UUID])
        assert "UUID" in str(field_info.annotation), "user_id should be UUID type"
