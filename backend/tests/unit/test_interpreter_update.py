"""
Unit tests for UPDATE intent extraction in AIInterpreter.

Tests the interpretation of natural language task update commands.

User Story 4: Natural Language Task Updates
"""

import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.ai.interpreter import AIInterpreter
from src.ai.types import CommandAction, ConfidenceLevel
from src.config.ai_config import AIConfig


@pytest.fixture
def interpreter():
    """Create interpreter with test config."""
    config = AIConfig(
        openai_api_key="test-key",
        ai_timeout_seconds=5.0,
    )
    return AIInterpreter(config=config)


@pytest.fixture
def mock_openai_update_title_response():
    """Mock OpenAI response for update title."""
    return {
        "action": "update",
        "confidence": 0.92,
        "task_id": 1,
        "title": "Call mom tonight",
        "needs_clarification": False,
    }


@pytest.fixture
def mock_openai_update_due_date_response():
    """Mock OpenAI response for update due date."""
    return {
        "action": "update",
        "confidence": 0.90,
        "task_id": 1,
        "due_date": "tomorrow",
        "needs_clarification": False,
    }


@pytest.fixture
def mock_openai_update_ambiguous_response():
    """Mock OpenAI response for ambiguous update."""
    return {
        "action": "update",
        "confidence": 0.4,
        "task_id": None,
        "needs_clarification": True,
        "clarification_question": "Which task would you like to update?",
    }


@pytest.fixture
def sample_user_tasks():
    """Sample user tasks for reference."""
    return [
        {"id": str(uuid4()), "title": "Buy groceries", "is_completed": False},
        {"id": str(uuid4()), "title": "Call mom", "is_completed": False},
    ]


class TestUpdateIntentExtraction:
    """Tests for UPDATE action intent extraction."""

    @pytest.mark.asyncio
    async def test_extract_update_title_intent(self, interpreter, mock_openai_update_title_response, sample_user_tasks):
        """Test extraction of update title command."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_update_title_response

            result = await interpreter.interpret(
                user_message="Change task 1 title to 'Call mom tonight'",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert result.action == CommandAction.UPDATE
            assert result.title == "Call mom tonight"
            assert result.confidence >= 0.8
            assert result.confidence_level == ConfidenceLevel.HIGH

    @pytest.mark.asyncio
    async def test_extract_update_due_date_intent(self, interpreter, mock_openai_update_due_date_response, sample_user_tasks):
        """Test extraction of update due date command."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_update_due_date_response

            result = await interpreter.interpret(
                user_message="Move task 1 to tomorrow",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert result.action == CommandAction.UPDATE
            assert result.due_date is not None
            expected_date = date.today() + timedelta(days=1)
            assert result.due_date == expected_date

    @pytest.mark.asyncio
    async def test_extract_update_ambiguous_needs_clarification(
        self, interpreter, mock_openai_update_ambiguous_response
    ):
        """Test that ambiguous update commands request clarification."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_update_ambiguous_response

            result = await interpreter.interpret(
                user_message="update it",
                user_id=uuid4(),
            )

            assert result.action == CommandAction.UPDATE
            assert result.needs_clarification is True
            assert result.clarification_needed is not None
            assert result.confidence_level == ConfidenceLevel.LOW

    @pytest.mark.asyncio
    async def test_suggested_cli_for_update_title(self, interpreter, mock_openai_update_title_response, sample_user_tasks):
        """Test that suggested CLI command is generated correctly for title update."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_update_title_response

            result = await interpreter.interpret(
                user_message="Update task 1 title to 'New title'",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert "bonsai update" in result.suggested_cli
            assert "--title" in result.suggested_cli

    @pytest.mark.asyncio
    async def test_suggested_cli_for_update_due_date(self, interpreter, mock_openai_update_due_date_response, sample_user_tasks):
        """Test that suggested CLI includes due date flag."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_update_due_date_response

            result = await interpreter.interpret(
                user_message="Move task 1 to tomorrow",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert "bonsai update" in result.suggested_cli
            assert "--due" in result.suggested_cli

    @pytest.mark.asyncio
    async def test_update_is_executable_with_task_id_and_changes(self, interpreter, sample_user_tasks):
        """Test that update with task ID and changes is executable."""
        response = {
            "action": "update",
            "confidence": 0.95,
            "task_id": 1,
            "title": "New title",
            "needs_clarification": False,
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message="Update task 1 to 'New title'",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert result.is_executable is True

    @pytest.mark.asyncio
    async def test_update_not_executable_without_task_id(self, interpreter):
        """Test that update without task ID is not executable."""
        response = {
            "action": "update",
            "confidence": 0.5,
            "task_id": None,
            "needs_clarification": True,
            "clarification_question": "Which task?",
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message="update something",
                user_id=uuid4(),
            )

            assert result.is_executable is False


class TestUpdateIntentVariations:
    """Test various natural language patterns for update intent."""

    @pytest.fixture
    def base_update_response(self):
        """Base response for update variations."""
        return {
            "action": "update",
            "confidence": 0.9,
            "task_id": 1,
            "title": "Updated title",
            "needs_clarification": False,
        }

    @pytest.fixture
    def sample_tasks(self):
        """Sample tasks for testing."""
        return [
            {"id": str(uuid4()), "title": "Test task", "is_completed": False},
        ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message", [
        "Change task 1 title to 'New title'",
        "Update task 1 to 'New title'",
        "Rename task 1 to 'New title'",
        "Edit task 1",
        "Modify task 1 title",
        "Set task 1 title to 'New title'",
    ])
    async def test_various_update_title_phrases(
        self, interpreter, base_update_response, sample_tasks, message
    ):
        """Test that various update phrases are recognized."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = base_update_response

            result = await interpreter.interpret(
                user_message=message,
                user_id=uuid4(),
                user_tasks=sample_tasks,
            )

            assert result.action == CommandAction.UPDATE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message", [
        "Move task 1 to tomorrow",
        "Change task 1 due date to next week",
        "Reschedule task 1 to Friday",
        "Push task 1 to next week",
    ])
    async def test_various_update_due_date_phrases(
        self, interpreter, sample_tasks, message
    ):
        """Test various due date update phrases."""
        response = {
            "action": "update",
            "confidence": 0.9,
            "task_id": 1,
            "due_date": "tomorrow",
            "needs_clarification": False,
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message=message,
                user_id=uuid4(),
                user_tasks=sample_tasks,
            )

            assert result.action == CommandAction.UPDATE


class TestCLICommandGenerationUpdate:
    """Tests for CLI command generation for update action."""

    @pytest.fixture
    def interpreter(self):
        """Create interpreter for CLI tests."""
        config = AIConfig(openai_api_key="test-key")
        return AIInterpreter(config=config)

    def test_build_update_cli_with_title(self, interpreter):
        """Test building update CLI command with title."""
        task_id = uuid4()
        result = interpreter._build_cli_command(
            action=CommandAction.UPDATE,
            title="New title",
            task_id=task_id,
            due_date=None,
            status_filter=None,
        )

        assert f"bonsai update {task_id}" in result
        assert '--title "New title"' in result

    def test_build_update_cli_with_due_date(self, interpreter):
        """Test building update CLI command with due date."""
        task_id = uuid4()
        due = date(2026, 2, 15)
        result = interpreter._build_cli_command(
            action=CommandAction.UPDATE,
            title=None,
            task_id=task_id,
            due_date=due,
            status_filter=None,
        )

        assert f"bonsai update {task_id}" in result
        assert "--due 2026-02-15" in result

    def test_build_update_cli_with_both(self, interpreter):
        """Test building update CLI command with both title and due date."""
        task_id = uuid4()
        due = date(2026, 2, 15)
        result = interpreter._build_cli_command(
            action=CommandAction.UPDATE,
            title="New title",
            task_id=task_id,
            due_date=due,
            status_filter=None,
        )

        assert f"bonsai update {task_id}" in result
        assert '--title "New title"' in result
        assert "--due 2026-02-15" in result

    def test_build_update_cli_without_task_id(self, interpreter):
        """Test building update CLI command without task ID."""
        result = interpreter._build_cli_command(
            action=CommandAction.UPDATE,
            title="New title",
            task_id=None,
            due_date=None,
            status_filter=None,
        )

        assert "bonsai update <task_id>" in result
