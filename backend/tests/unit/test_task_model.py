"""
Unit tests for Task model and schemas.

Tests:
- T023: Task model creation (UUID, defaults, timestamps)
- T024: TaskCreate validation (title length, description max)
- T025: TaskUpdate schema (partial updates)
- T026: TaskPublic schema (all fields included)
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID


# =============================================================================
# T023: Task Model Creation Tests
# =============================================================================

@pytest.mark.unit
class TestTaskModelCreation:
    """Test Task model creation with UUID, defaults, and timestamps."""

    def test_task_has_uuid_id(self, valid_task_title: str) -> None:
        """Task.id should be a valid UUID, auto-generated."""
        from src.models.task import Task
        from uuid import uuid4

        user_id = uuid4()
        task = Task(
            title=valid_task_title,
            user_id=user_id,
        )

        assert task.id is not None
        assert isinstance(task.id, UUID)

    def test_task_has_created_at_timestamp(self, valid_task_title: str) -> None:
        """Task.created_at should be auto-populated with UTC timestamp."""
        from src.models.task import Task
        from uuid import uuid4

        before = datetime.now(timezone.utc)
        task = Task(
            title=valid_task_title,
            user_id=uuid4(),
        )
        after = datetime.now(timezone.utc)

        assert task.created_at is not None
        assert isinstance(task.created_at, datetime)
        assert before <= task.created_at <= after

    def test_task_has_updated_at_timestamp(self, valid_task_title: str) -> None:
        """Task.updated_at should be auto-populated with UTC timestamp."""
        from src.models.task import Task
        from uuid import uuid4

        task = Task(
            title=valid_task_title,
            user_id=uuid4(),
        )

        assert task.updated_at is not None
        assert isinstance(task.updated_at, datetime)

    def test_task_is_completed_defaults_false(self, valid_task_title: str) -> None:
        """Task.is_completed should default to False."""
        from src.models.task import Task
        from uuid import uuid4

        task = Task(
            title=valid_task_title,
            user_id=uuid4(),
        )

        assert task.is_completed is False

    def test_task_description_nullable(self, valid_task_title: str) -> None:
        """Task.description should be nullable (None by default)."""
        from src.models.task import Task
        from uuid import uuid4

        task = Task(
            title=valid_task_title,
            user_id=uuid4(),
        )

        assert task.description is None

    def test_task_stores_user_id(self, valid_task_title: str) -> None:
        """Task should store user_id correctly."""
        from src.models.task import Task
        from uuid import uuid4

        user_id = uuid4()
        task = Task(
            title=valid_task_title,
            user_id=user_id,
        )

        assert task.user_id == user_id


# =============================================================================
# T024: TaskCreate Validation Tests
# =============================================================================

@pytest.mark.unit
class TestTaskCreateValidation:
    """Test TaskCreate schema validation."""

    def test_valid_task_create(self, valid_task_title: str) -> None:
        """TaskCreate should accept valid title."""
        from src.models.task import TaskCreate

        task_create = TaskCreate(title=valid_task_title)

        assert task_create.title == valid_task_title

    def test_task_create_with_description(
        self, valid_task_title: str, valid_task_description: str
    ) -> None:
        """TaskCreate should accept optional description."""
        from src.models.task import TaskCreate

        task_create = TaskCreate(
            title=valid_task_title,
            description=valid_task_description,
        )

        assert task_create.description == valid_task_description

    def test_empty_title_rejected(self) -> None:
        """TaskCreate should reject empty title."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")

        errors = exc_info.value.errors()
        assert any("title" in str(e.get("loc", [])) for e in errors)

    def test_title_too_long_rejected(self, invalid_task_titles: list[str]) -> None:
        """TaskCreate should reject title exceeding 255 characters."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        long_title = "x" * 256
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title)

        errors = exc_info.value.errors()
        assert any("title" in str(e.get("loc", [])) for e in errors)

    def test_title_max_length_accepted(self) -> None:
        """TaskCreate should accept title with exactly 255 characters."""
        from src.models.task import TaskCreate

        max_title = "x" * 255
        task_create = TaskCreate(title=max_title)

        assert len(task_create.title) == 255

    def test_description_too_long_rejected(
        self, valid_task_title: str, invalid_task_descriptions: list[str]
    ) -> None:
        """TaskCreate should reject description exceeding 4000 characters."""
        from pydantic import ValidationError
        from src.models.task import TaskCreate

        long_description = "x" * 4001
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=valid_task_title, description=long_description)

        errors = exc_info.value.errors()
        assert any("description" in str(e.get("loc", [])) for e in errors)

    def test_description_max_length_accepted(self, valid_task_title: str) -> None:
        """TaskCreate should accept description with exactly 4000 characters."""
        from src.models.task import TaskCreate

        max_description = "x" * 4000
        task_create = TaskCreate(title=valid_task_title, description=max_description)

        assert len(task_create.description) == 4000


# =============================================================================
# T025: TaskUpdate Schema Tests
# =============================================================================

@pytest.mark.unit
class TestTaskUpdateSchema:
    """Test TaskUpdate schema for partial updates."""

    def test_task_update_all_fields_optional(self) -> None:
        """TaskUpdate should allow all fields to be None (partial update)."""
        from src.models.task import TaskUpdate

        task_update = TaskUpdate()

        assert task_update.title is None
        assert task_update.description is None
        assert task_update.is_completed is None

    def test_task_update_title_only(self) -> None:
        """TaskUpdate should allow updating only title."""
        from src.models.task import TaskUpdate

        task_update = TaskUpdate(title="New Title")

        assert task_update.title == "New Title"
        assert task_update.description is None
        assert task_update.is_completed is None

    def test_task_update_is_completed_only(self) -> None:
        """TaskUpdate should allow updating only is_completed."""
        from src.models.task import TaskUpdate

        task_update = TaskUpdate(is_completed=True)

        assert task_update.title is None
        assert task_update.description is None
        assert task_update.is_completed is True

    def test_task_update_description_only(self) -> None:
        """TaskUpdate should allow updating only description."""
        from src.models.task import TaskUpdate

        task_update = TaskUpdate(description="New description")

        assert task_update.title is None
        assert task_update.description == "New description"
        assert task_update.is_completed is None


# =============================================================================
# T026: TaskPublic Schema Tests
# =============================================================================

@pytest.mark.unit
class TestTaskPublicSchema:
    """Test TaskPublic schema includes all required fields."""

    def test_task_public_has_all_fields(self, valid_task_title: str) -> None:
        """TaskPublic should include id, user_id, title, description, is_completed, timestamps."""
        from src.models.task import Task, TaskPublic
        from uuid import uuid4
        from datetime import datetime, timezone

        user_id = uuid4()
        task_id = uuid4()
        created = datetime.now(timezone.utc)
        updated = datetime.now(timezone.utc)

        task = Task(
            id=task_id,
            user_id=user_id,
            title=valid_task_title,
            description="Test description",
            is_completed=False,
            created_at=created,
            updated_at=updated,
        )

        task_public = TaskPublic.model_validate(task)

        assert task_public.id == task_id
        assert task_public.user_id == user_id
        assert task_public.title == valid_task_title
        assert task_public.description == "Test description"
        assert task_public.is_completed is False
        assert task_public.created_at == created
        assert task_public.updated_at == updated

    def test_task_public_json_serialization(self, valid_task_title: str) -> None:
        """TaskPublic should serialize to JSON with all fields."""
        from src.models.task import TaskPublic
        from uuid import uuid4
        from datetime import datetime, timezone

        task_public = TaskPublic(
            id=uuid4(),
            user_id=uuid4(),
            title=valid_task_title,
            description="Test",
            is_completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        json_data = task_public.model_dump(mode="json")

        assert "id" in json_data
        assert "user_id" in json_data
        assert "title" in json_data
        assert "description" in json_data
        assert "is_completed" in json_data
        assert "created_at" in json_data
        assert "updated_at" in json_data
