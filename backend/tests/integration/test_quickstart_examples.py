"""
Integration tests validating quickstart.md examples work correctly.

Tests:
- T056: Validate all models against quickstart.md examples
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4


@pytest.mark.integration
class TestQuickstartUserExamples:
    """Test User examples from quickstart.md."""

    def test_user_create_example(self) -> None:
        """Test UserCreate example from quickstart.md."""
        from src.models.user import UserCreate

        # From quickstart: Valid user
        user_create = UserCreate(email="user@example.com", password="password123")

        assert user_create.email == "user@example.com"
        assert user_create.password == "password123"

    def test_user_model_creation(self) -> None:
        """Test User model creation as shown in quickstart.md."""
        from src.models.user import User, UserCreate
        from src.auth.password import hash_password

        user_create = UserCreate(email="user@example.com", password="securepass123")
        user = User(
            email=user_create.email,
            password_hash=hash_password(user_create.password)
        )

        assert user.email == "user@example.com"
        assert user.password_hash != "securepass123"  # Should be hashed
        assert user.id is not None  # Auto-generated
        assert user.created_at is not None  # Auto-generated
        assert user.updated_at is not None  # Auto-generated

    def test_invalid_email_example(self) -> None:
        """Test invalid email validation from quickstart.md."""
        from pydantic import ValidationError
        from src.models.user import UserCreate

        # From quickstart: Invalid email
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", password="password123")


@pytest.mark.integration
class TestQuickstartTaskExamples:
    """Test Task examples from quickstart.md."""

    def test_task_create_minimal(self) -> None:
        """Test minimal TaskCreate from quickstart.md."""
        from src.models.task import TaskCreate

        # From quickstart: minimum title
        task_create = TaskCreate(title="A", description=None)

        assert task_create.title == "A"
        assert task_create.description is None
        assert task_create.is_completed is False

    def test_task_create_full(self) -> None:
        """Test full TaskCreate from quickstart.md."""
        from src.models.task import TaskCreate

        # From quickstart: full example
        task_create = TaskCreate(title="Buy groceries", description="Milk, eggs")

        assert task_create.title == "Buy groceries"
        assert task_create.description == "Milk, eggs"

    def test_task_model_creation(self) -> None:
        """Test Task model creation as shown in quickstart.md."""
        from src.models.task import Task, TaskCreate

        task_create = TaskCreate(title="Buy groceries", description="Milk, eggs")
        user_id = uuid4()

        task = Task(
            **task_create.model_dump(),
            user_id=user_id
        )

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs"
        assert task.user_id == user_id
        assert task.id is not None  # Auto-generated
        assert task.is_completed is False  # Default

    def test_empty_title_example(self) -> None:
        """Test empty title validation from quickstart.md."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        # From quickstart: Empty title
        with pytest.raises(ValidationError):
            TaskCreate(title="", description="Details")

    def test_title_too_long_example(self) -> None:
        """Test title too long validation from quickstart.md."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        # From quickstart: Title too long
        with pytest.raises(ValidationError):
            TaskCreate(title="x" * 256, description=None)

    def test_description_too_long_example(self) -> None:
        """Test description too long validation from quickstart.md."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        # From quickstart: Description too long
        with pytest.raises(ValidationError):
            TaskCreate(title="Task", description="x" * 4001)


@pytest.mark.integration
class TestQuickstartTaskUpdateExamples:
    """Test TaskUpdate examples from quickstart.md."""

    def test_task_update_partial(self) -> None:
        """Test partial update as shown in quickstart.md."""
        from src.models.task import TaskUpdate

        # From quickstart: Update is_completed only
        task_update = TaskUpdate(is_completed=True)

        # Verify exclude_unset works as documented
        update_data = task_update.model_dump(exclude_unset=True)

        assert "is_completed" in update_data
        assert update_data["is_completed"] is True
        assert "title" not in update_data
        assert "description" not in update_data

    def test_task_update_apply(self) -> None:
        """Test applying update to existing task as shown in quickstart.md."""
        from src.models.task import Task, TaskUpdate

        # Create a task
        task = Task(
            title="Original",
            description="Original desc",
            is_completed=False,
            user_id=uuid4(),
        )

        # Update as shown in quickstart
        task_update = TaskUpdate(is_completed=True)
        for key, value in task_update.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        task.updated_at = datetime.now(timezone.utc)

        # Verify update applied correctly
        assert task.title == "Original"  # Unchanged
        assert task.description == "Original desc"  # Unchanged
        assert task.is_completed is True  # Updated


@pytest.mark.integration
class TestQuickstartPasswordExamples:
    """Test password hashing examples from quickstart.md."""

    def test_hash_password_example(self) -> None:
        """Test hash_password from quickstart.md."""
        from src.auth.password import hash_password

        # From quickstart
        password = "securepass123"
        hashed = hash_password(password)

        assert hashed != password
        assert hashed.startswith("$argon2")

    def test_verify_password_example(self) -> None:
        """Test verify_password from quickstart.md."""
        from src.auth.password import hash_password, verify_password

        password = "securepass123"
        hashed = hash_password(password)

        assert verify_password(hashed, password) is True
        assert verify_password(hashed, "wrong") is False


@pytest.mark.integration
class TestQuickstartPublicSchemaExamples:
    """Test public schema examples from quickstart.md."""

    def test_user_public_from_user(self) -> None:
        """Test UserPublic creation from User model."""
        from src.models.user import User, UserPublic

        user = User(
            email="user@example.com",
            password_hash="$argon2..."
        )

        user_public = UserPublic.model_validate(user)

        assert user_public.id == user.id
        assert user_public.email == user.email
        assert not hasattr(user_public, "password_hash")

    def test_task_public_from_task(self) -> None:
        """Test TaskPublic creation from Task model."""
        from src.models.task import Task, TaskPublic

        task = Task(
            title="Buy groceries",
            description="Milk, eggs",
            user_id=uuid4(),
        )

        task_public = TaskPublic.model_validate(task)

        assert task_public.id == task.id
        assert task_public.title == task.title
        assert task_public.description == task.description
        assert task_public.user_id == task.user_id
        assert task_public.is_completed == task.is_completed


@pytest.mark.integration
class TestQuickstartModuleImports:
    """Test that imports work as shown in quickstart.md."""

    def test_models_importable(self) -> None:
        """Test model imports work."""
        from src.models.user import User, UserCreate, UserPublic, UserBase
        from src.models.task import Task, TaskCreate, TaskUpdate, TaskPublic, TaskBase

        # All should be importable
        assert User is not None
        assert UserCreate is not None
        assert UserPublic is not None
        assert Task is not None
        assert TaskCreate is not None
        assert TaskUpdate is not None
        assert TaskPublic is not None

    def test_auth_importable(self) -> None:
        """Test auth imports work."""
        from src.auth.password import hash_password, verify_password

        assert hash_password is not None
        assert verify_password is not None

    def test_package_exports(self) -> None:
        """Test models package exports all models."""
        from src.models import (
            User, UserBase, UserCreate, UserPublic,
            Task, TaskBase, TaskCreate, TaskUpdate, TaskPublic,
        )

        assert User is not None
        assert Task is not None
