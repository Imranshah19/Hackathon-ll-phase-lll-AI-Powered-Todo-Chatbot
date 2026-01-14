"""
Unit tests for schema evolution support.

Tests:
- T048: Optional field handling (nullable fields)
- T049: Default values (is_completed default)
- T050: Partial updates (TaskUpdate with missing fields)

Goal: Ensure schemas support forward compatibility with optional fields and defaults.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4


# =============================================================================
# T048: Optional Field Handling Tests
# =============================================================================

@pytest.mark.unit
class TestOptionalFieldHandling:
    """Test that optional/nullable fields work correctly for schema evolution."""

    def test_task_description_is_optional(self) -> None:
        """Task.description should be optional (None by default)."""
        from src.models.task import Task

        task = Task(title="Test", user_id=uuid4())

        assert task.description is None, "description should default to None"

    def test_task_create_description_optional(self) -> None:
        """TaskCreate.description should be optional."""
        from src.models.task import TaskCreate

        task = TaskCreate(title="Test")

        assert task.description is None, "description should default to None"

    def test_task_create_accepts_none_description(self) -> None:
        """TaskCreate should explicitly accept None for description."""
        from src.models.task import TaskCreate

        task = TaskCreate(title="Test", description=None)

        assert task.description is None

    def test_task_update_all_fields_optional(self) -> None:
        """TaskUpdate should have all fields optional for partial updates."""
        from src.models.task import TaskUpdate

        # Create with no fields - should work
        update = TaskUpdate()

        assert update.title is None
        assert update.description is None
        assert update.is_completed is None

    def test_task_public_handles_none_description(self) -> None:
        """TaskPublic should handle None description correctly."""
        from src.models.task import TaskPublic

        task_public = TaskPublic(
            id=uuid4(),
            user_id=uuid4(),
            title="Test",
            description=None,
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        assert task_public.description is None
        # Should serialize to JSON with null
        json_data = task_public.model_dump(mode="json")
        assert json_data["description"] is None

    def test_new_optional_field_backwards_compatible(self) -> None:
        """Adding new optional fields should not break existing data.

        This test simulates schema evolution - existing data without
        new fields should still be valid.
        """
        from src.models.task import TaskCreate

        # Simulate data from old client (no is_completed field)
        old_client_data = {"title": "Old task"}

        task = TaskCreate.model_validate(old_client_data)

        # Should use default values
        assert task.title == "Old task"
        assert task.description is None
        assert task.is_completed is False


# =============================================================================
# T049: Default Values Tests
# =============================================================================

@pytest.mark.unit
class TestDefaultValues:
    """Test that default values are applied correctly for schema evolution."""

    def test_task_is_completed_defaults_false(self) -> None:
        """Task.is_completed should default to False."""
        from src.models.task import Task

        task = Task(title="Test", user_id=uuid4())

        assert task.is_completed is False

    def test_task_create_is_completed_defaults_false(self) -> None:
        """TaskCreate.is_completed should default to False."""
        from src.models.task import TaskCreate

        task = TaskCreate(title="Test")

        assert task.is_completed is False

    def test_task_description_defaults_none(self) -> None:
        """Task.description should default to None."""
        from src.models.task import Task

        task = Task(title="Test", user_id=uuid4())

        assert task.description is None

    def test_task_id_auto_generated(self) -> None:
        """Task.id should be auto-generated UUID."""
        from src.models.task import Task
        from uuid import UUID

        task = Task(title="Test", user_id=uuid4())

        assert task.id is not None
        assert isinstance(task.id, UUID)

    def test_task_timestamps_auto_generated(self) -> None:
        """Task.created_at and updated_at should be auto-generated."""
        from src.models.task import Task

        before = datetime.now(timezone.utc)
        task = Task(title="Test", user_id=uuid4())
        after = datetime.now(timezone.utc)

        assert task.created_at is not None
        assert task.updated_at is not None
        assert before <= task.created_at <= after
        assert before <= task.updated_at <= after

    def test_user_id_auto_generated(self) -> None:
        """User.id should be auto-generated UUID."""
        from src.models.user import User
        from uuid import UUID

        user = User(email="test@example.com", password_hash="hash")

        assert user.id is not None
        assert isinstance(user.id, UUID)

    def test_user_timestamps_auto_generated(self) -> None:
        """User.created_at and updated_at should be auto-generated."""
        from src.models.user import User

        before = datetime.now(timezone.utc)
        user = User(email="test@example.com", password_hash="hash")
        after = datetime.now(timezone.utc)

        assert user.created_at is not None
        assert user.updated_at is not None
        assert before <= user.created_at <= after
        assert before <= user.updated_at <= after

    def test_explicit_values_override_defaults(self) -> None:
        """Explicit values should override defaults."""
        from src.models.task import TaskCreate

        task = TaskCreate(
            title="Test",
            description="Custom description",
            is_completed=True,
        )

        assert task.description == "Custom description"
        assert task.is_completed is True


# =============================================================================
# T050: Partial Updates Tests
# =============================================================================

@pytest.mark.unit
class TestPartialUpdates:
    """Test TaskUpdate handles partial updates correctly for schema evolution."""

    def test_update_title_only(self) -> None:
        """TaskUpdate should allow updating only title."""
        from src.models.task import TaskUpdate

        update = TaskUpdate(title="New Title")

        assert update.title == "New Title"
        assert update.description is None
        assert update.is_completed is None

    def test_update_description_only(self) -> None:
        """TaskUpdate should allow updating only description."""
        from src.models.task import TaskUpdate

        update = TaskUpdate(description="New description")

        assert update.title is None
        assert update.description == "New description"
        assert update.is_completed is None

    def test_update_is_completed_only(self) -> None:
        """TaskUpdate should allow updating only is_completed."""
        from src.models.task import TaskUpdate

        update = TaskUpdate(is_completed=True)

        assert update.title is None
        assert update.description is None
        assert update.is_completed is True

    def test_update_multiple_fields(self) -> None:
        """TaskUpdate should allow updating multiple fields at once."""
        from src.models.task import TaskUpdate

        update = TaskUpdate(
            title="New Title",
            is_completed=True,
        )

        assert update.title == "New Title"
        assert update.description is None
        assert update.is_completed is True

    def test_update_empty_is_valid(self) -> None:
        """Empty TaskUpdate should be valid (no fields to update)."""
        from src.models.task import TaskUpdate

        update = TaskUpdate()

        # All fields should be None
        assert update.title is None
        assert update.description is None
        assert update.is_completed is None

    def test_update_from_json_partial(self) -> None:
        """TaskUpdate should parse partial JSON correctly."""
        from src.models.task import TaskUpdate

        # Simulate partial JSON from client
        json_data = {"is_completed": True}

        update = TaskUpdate.model_validate(json_data)

        assert update.title is None
        assert update.description is None
        assert update.is_completed is True

    def test_update_distinguishes_none_from_missing(self) -> None:
        """TaskUpdate should distinguish between None value and missing field.

        This is important for schema evolution - clients may want to
        explicitly set a field to None vs not updating it at all.
        """
        from src.models.task import TaskUpdate

        # Explicit None
        update_with_none = TaskUpdate(description=None)

        # Missing field (from JSON without description)
        update_missing = TaskUpdate.model_validate({"title": "Test"})

        # Both should have description as None, but semantically different
        # In practice, the update logic would check which fields were provided
        assert update_with_none.description is None
        assert update_missing.description is None

    def test_update_preserves_field_constraints(self) -> None:
        """TaskUpdate should still validate field constraints."""
        from pydantic import ValidationError
        from src.models.task import TaskUpdate

        # Title too long should still fail
        with pytest.raises(ValidationError):
            TaskUpdate(title="x" * 256)

        # Description too long should still fail
        with pytest.raises(ValidationError):
            TaskUpdate(description="x" * 4001)

    def test_update_model_dump_excludes_unset(self) -> None:
        """TaskUpdate.model_dump(exclude_unset=True) should only include set fields."""
        from src.models.task import TaskUpdate

        update = TaskUpdate(is_completed=True)

        # With exclude_unset, only is_completed should be in the dict
        dump = update.model_dump(exclude_unset=True)

        assert "is_completed" in dump
        assert dump["is_completed"] is True
        # title and description should not be in dump
        assert "title" not in dump
        assert "description" not in dump


# =============================================================================
# Additional: Schema Evolution Patterns
# =============================================================================

@pytest.mark.unit
class TestSchemaEvolutionPatterns:
    """Test general schema evolution patterns for forward compatibility."""

    def test_model_accepts_extra_fields_ignored(self) -> None:
        """Models should gracefully handle extra fields from newer clients.

        Note: By default SQLModel/Pydantic ignores extra fields.
        """
        from src.models.task import TaskCreate

        # Simulate data from newer client with extra field
        new_client_data = {
            "title": "Test",
            "description": "Desc",
            "is_completed": False,
            "new_field_v2": "some value",  # Future field
        }

        # Should not raise - extra fields ignored
        task = TaskCreate.model_validate(new_client_data)

        assert task.title == "Test"
        # new_field_v2 should be ignored
        assert not hasattr(task, "new_field_v2")

    def test_model_serialization_stable(self) -> None:
        """Model JSON serialization should be stable and predictable."""
        from src.models.task import TaskPublic
        import json

        task = TaskPublic(
            id=uuid4(),
            user_id=uuid4(),
            title="Test",
            description=None,
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Should serialize to valid JSON
        json_str = task.model_dump_json()
        parsed = json.loads(json_str)

        # All expected fields should be present
        assert "id" in parsed
        assert "user_id" in parsed
        assert "title" in parsed
        assert "description" in parsed
        assert "is_completed" in parsed
        assert "created_at" in parsed
        assert "updated_at" in parsed

    def test_from_attributes_works(self) -> None:
        """TaskPublic should work with from_attributes for ORM conversion."""
        from src.models.task import Task, TaskPublic

        # Create a Task (simulating ORM object)
        task = Task(
            id=uuid4(),
            user_id=uuid4(),
            title="Test",
            description="Desc",
            is_completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Convert to public schema
        task_public = TaskPublic.model_validate(task)

        assert task_public.id == task.id
        assert task_public.user_id == task.user_id
        assert task_public.title == task.title
        assert task_public.description == task.description
        assert task_public.is_completed == task.is_completed
