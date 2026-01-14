"""
Contract tests for Task schemas.

Tests:
- T027: Validate Task schemas match OpenAPI specification
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4


@pytest.mark.contract
class TestTaskSchemaContract:
    """Contract tests ensuring Task schemas match API specification."""

    def test_task_public_has_required_fields(self) -> None:
        """TaskPublic must have: id, user_id, title, description, is_completed, created_at, updated_at."""
        from src.models.task import TaskPublic

        fields = TaskPublic.model_fields

        required_fields = [
            "id",
            "user_id",
            "title",
            "description",
            "is_completed",
            "created_at",
            "updated_at",
        ]
        for field in required_fields:
            assert field in fields, f"TaskPublic missing required field: {field}"

    def test_task_create_has_required_fields(self) -> None:
        """TaskCreate must have: title. Optional: description, is_completed."""
        from src.models.task import TaskCreate

        fields = TaskCreate.model_fields

        assert "title" in fields, "TaskCreate missing required field: title"
        # user_id should NOT be in TaskCreate (injected from auth context)
        assert "user_id" not in fields, "TaskCreate should not have user_id"

    def test_task_update_all_fields_optional(self) -> None:
        """TaskUpdate must have all fields optional for partial updates."""
        from src.models.task import TaskUpdate

        fields = TaskUpdate.model_fields

        # All fields should be optional (allow None)
        expected_fields = ["title", "description", "is_completed"]
        for field in expected_fields:
            assert field in fields, f"TaskUpdate missing field: {field}"

    def test_task_public_json_serialization(self) -> None:
        """TaskPublic should serialize to JSON matching OpenAPI spec."""
        from src.models.task import TaskPublic

        task_public = TaskPublic(
            id=uuid4(),
            user_id=uuid4(),
            title="Test task",
            description="Test description",
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        json_data = task_public.model_dump(mode="json")

        # Check JSON structure matches OpenAPI
        assert "id" in json_data
        assert "user_id" in json_data
        assert "title" in json_data
        assert "description" in json_data
        assert "is_completed" in json_data
        assert "created_at" in json_data
        assert "updated_at" in json_data

        # id and user_id should be strings (UUID serialized)
        assert isinstance(json_data["id"], str)
        assert isinstance(json_data["user_id"], str)
        # title and description should be strings
        assert isinstance(json_data["title"], str)
        # is_completed should be boolean
        assert isinstance(json_data["is_completed"], bool)
        # timestamps should be ISO format strings
        assert isinstance(json_data["created_at"], str)
        assert isinstance(json_data["updated_at"], str)

    def test_task_create_accepts_valid_input(self) -> None:
        """TaskCreate should accept valid JSON input."""
        from src.models.task import TaskCreate

        input_data = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "is_completed": False,
        }

        task_create = TaskCreate.model_validate(input_data)

        assert task_create.title == input_data["title"]
        assert task_create.description == input_data["description"]
        assert task_create.is_completed == input_data["is_completed"]

    def test_task_create_minimal_input(self) -> None:
        """TaskCreate should accept minimal input (title only)."""
        from src.models.task import TaskCreate

        input_data = {"title": "Simple task"}

        task_create = TaskCreate.model_validate(input_data)

        assert task_create.title == "Simple task"
        # Description should default to None
        assert task_create.description is None
        # is_completed should default to False
        assert task_create.is_completed is False

    def test_task_id_is_uuid_format(self) -> None:
        """Task.id should be UUID v4 format."""
        from src.models.task import Task

        task = Task(
            title="Test task",
            user_id=uuid4(),
        )

        # UUID should be version 4
        assert task.id.version == 4

    def test_task_title_length_validation(self) -> None:
        """TaskCreate.title should validate length (1-255 chars) per OpenAPI."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        # Empty title should be rejected
        with pytest.raises(ValidationError):
            TaskCreate(title="")

        # Title over 255 chars should be rejected
        with pytest.raises(ValidationError):
            TaskCreate(title="x" * 256)

        # Title at boundary (255 chars) should be accepted
        task = TaskCreate(title="x" * 255)
        assert len(task.title) == 255

    def test_task_description_length_validation(self) -> None:
        """TaskCreate.description should validate max length (4000 chars) per OpenAPI."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        # Description over 4000 chars should be rejected
        with pytest.raises(ValidationError):
            TaskCreate(title="Test", description="x" * 4001)

        # Description at boundary (4000 chars) should be accepted
        task = TaskCreate(title="Test", description="x" * 4000)
        assert len(task.description) == 4000
