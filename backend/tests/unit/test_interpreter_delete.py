"""
Unit tests for DELETE intent extraction in AIInterpreter.

Tests the interpretation of natural language task deletion commands.

User Story 5: Natural Language Task Deletion
"""

import pytest
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
def mock_openai_delete_by_id_response():
    """Mock OpenAI response for delete by ID."""
    return {
        "action": "delete",
        "confidence": 0.95,
        "task_id": 1,
        "needs_clarification": False,
    }


@pytest.fixture
def mock_openai_delete_by_reference_response():
    """Mock OpenAI response for delete by title reference."""
    return {
        "action": "delete",
        "confidence": 0.88,
        "task_reference": "groceries",
        "needs_clarification": False,
    }


@pytest.fixture
def mock_openai_delete_ambiguous_response():
    """Mock OpenAI response for ambiguous delete."""
    return {
        "action": "delete",
        "confidence": 0.4,
        "task_id": None,
        "needs_clarification": True,
        "clarification_question": "Which task would you like to delete?",
    }


@pytest.fixture
def sample_user_tasks():
    """Sample user tasks for reference."""
    return [
        {"id": str(uuid4()), "title": "Buy groceries", "is_completed": False},
        {"id": str(uuid4()), "title": "Call mom", "is_completed": False},
    ]


class TestDeleteIntentExtraction:
    """Tests for DELETE action intent extraction."""

    @pytest.mark.asyncio
    async def test_extract_delete_by_id(self, interpreter, mock_openai_delete_by_id_response, sample_user_tasks):
        """Test extraction of delete command by ID."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_delete_by_id_response

            result = await interpreter.interpret(
                user_message="Delete task 1",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert result.action == CommandAction.DELETE
            assert result.confidence >= 0.8
            assert result.confidence_level == ConfidenceLevel.HIGH

    @pytest.mark.asyncio
    async def test_extract_delete_by_title_reference(
        self, interpreter, mock_openai_delete_by_reference_response, sample_user_tasks
    ):
        """Test extraction of delete command by title reference."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_delete_by_reference_response

            result = await interpreter.interpret(
                user_message="Remove the groceries task",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert result.action == CommandAction.DELETE
            assert result.task_id is not None

    @pytest.mark.asyncio
    async def test_extract_delete_ambiguous_needs_clarification(
        self, interpreter, mock_openai_delete_ambiguous_response
    ):
        """Test that ambiguous delete commands request clarification."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_delete_ambiguous_response

            result = await interpreter.interpret(
                user_message="delete it",
                user_id=uuid4(),
            )

            assert result.action == CommandAction.DELETE
            assert result.needs_clarification is True
            assert result.clarification_needed is not None
            assert result.confidence_level == ConfidenceLevel.LOW

    @pytest.mark.asyncio
    async def test_suggested_cli_for_delete(self, interpreter, sample_user_tasks):
        """Test that suggested CLI command is generated correctly."""
        response = {
            "action": "delete",
            "confidence": 0.95,
            "task_id": 1,
            "needs_clarification": False,
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message="Delete task 1",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert "bonsai delete" in result.suggested_cli

    @pytest.mark.asyncio
    async def test_delete_is_executable_with_task_id(self, interpreter, sample_user_tasks):
        """Test that delete with task ID is executable."""
        response = {
            "action": "delete",
            "confidence": 0.95,
            "task_id": 1,
            "needs_clarification": False,
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message="Delete task 1",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert result.is_executable is True

    @pytest.mark.asyncio
    async def test_delete_not_executable_without_task_id(self, interpreter):
        """Test that delete without task ID is not executable."""
        response = {
            "action": "delete",
            "confidence": 0.5,
            "task_id": None,
            "needs_clarification": True,
            "clarification_question": "Which task?",
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message="delete something",
                user_id=uuid4(),
            )

            assert result.is_executable is False


class TestDeleteIntentVariations:
    """Test various natural language patterns for delete intent."""

    @pytest.fixture
    def base_delete_response(self):
        """Base response for delete variations."""
        return {
            "action": "delete",
            "confidence": 0.9,
            "task_id": 1,
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
        "Delete task 1",
        "Remove task 1",
        "Get rid of task 1",
        "Erase task 1",
        "Cancel task 1",
        "Drop task 1",
        "Discard task 1",
    ])
    async def test_various_delete_phrases(
        self, interpreter, base_delete_response, sample_tasks, message
    ):
        """Test that various delete phrases are recognized."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = base_delete_response

            result = await interpreter.interpret(
                user_message=message,
                user_id=uuid4(),
                user_tasks=sample_tasks,
            )

            assert result.action == CommandAction.DELETE


class TestCLICommandGenerationDelete:
    """Tests for CLI command generation for delete action."""

    @pytest.fixture
    def interpreter(self):
        """Create interpreter for CLI tests."""
        config = AIConfig(openai_api_key="test-key")
        return AIInterpreter(config=config)

    def test_build_delete_cli_with_id(self, interpreter):
        """Test building delete CLI command with task ID."""
        task_id = uuid4()
        result = interpreter._build_cli_command(
            action=CommandAction.DELETE,
            title=None,
            task_id=task_id,
            due_date=None,
            status_filter=None,
        )

        assert f"bonsai delete {task_id}" == result

    def test_build_delete_cli_without_id(self, interpreter):
        """Test building delete CLI command without task ID."""
        result = interpreter._build_cli_command(
            action=CommandAction.DELETE,
            title=None,
            task_id=None,
            due_date=None,
            status_filter=None,
        )

        assert "bonsai delete <task_id>" == result
