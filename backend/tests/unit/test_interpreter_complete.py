"""
Unit tests for COMPLETE intent extraction in AIInterpreter.

Tests the interpretation of natural language task completion commands.

User Story 3: Natural Language Task Completion
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
def mock_openai_complete_by_id_response():
    """Mock OpenAI response for complete by ID."""
    return {
        "action": "complete",
        "confidence": 0.95,
        "task_id": 1,
        "needs_clarification": False,
    }


@pytest.fixture
def mock_openai_complete_by_reference_response():
    """Mock OpenAI response for complete by title reference."""
    return {
        "action": "complete",
        "confidence": 0.88,
        "task_reference": "groceries",
        "needs_clarification": False,
    }


@pytest.fixture
def mock_openai_complete_ambiguous_response():
    """Mock OpenAI response for ambiguous complete."""
    return {
        "action": "complete",
        "confidence": 0.4,
        "task_reference": "task",
        "needs_clarification": True,
        "clarification_question": "Which task would you like to complete?",
    }


@pytest.fixture
def sample_user_tasks():
    """Sample user tasks for reference matching."""
    return [
        {"id": str(uuid4()), "title": "Buy groceries", "is_completed": False},
        {"id": str(uuid4()), "title": "Call mom", "is_completed": False},
        {"id": str(uuid4()), "title": "Finish report", "is_completed": False},
    ]


class TestCompleteIntentExtraction:
    """Tests for COMPLETE action intent extraction."""

    @pytest.mark.asyncio
    async def test_extract_complete_by_id(self, interpreter, mock_openai_complete_by_id_response, sample_user_tasks):
        """Test extraction of complete command by ID."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_complete_by_id_response

            result = await interpreter.interpret(
                user_message="Mark task 1 as done",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert result.action == CommandAction.COMPLETE
            assert result.confidence >= 0.8
            assert result.confidence_level == ConfidenceLevel.HIGH

    @pytest.mark.asyncio
    async def test_extract_complete_by_title_reference(
        self, interpreter, mock_openai_complete_by_reference_response, sample_user_tasks
    ):
        """Test extraction of complete command by title reference."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_complete_by_reference_response

            result = await interpreter.interpret(
                user_message="I finished buying groceries",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert result.action == CommandAction.COMPLETE
            assert result.task_id is not None  # Should resolve to the groceries task

    @pytest.mark.asyncio
    async def test_extract_complete_ambiguous_needs_clarification(
        self, interpreter, mock_openai_complete_ambiguous_response
    ):
        """Test that ambiguous complete commands request clarification."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_complete_ambiguous_response

            result = await interpreter.interpret(
                user_message="mark it as done",
                user_id=uuid4(),
            )

            assert result.action == CommandAction.COMPLETE
            assert result.needs_clarification is True
            assert result.clarification_needed is not None
            assert result.confidence_level == ConfidenceLevel.LOW

    @pytest.mark.asyncio
    async def test_suggested_cli_for_complete(self, interpreter, sample_user_tasks):
        """Test that suggested CLI command is generated correctly."""
        response = {
            "action": "complete",
            "confidence": 0.95,
            "task_id": 1,
            "needs_clarification": False,
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message="Mark task 1 as done",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert "bonsai complete" in result.suggested_cli

    @pytest.mark.asyncio
    async def test_complete_is_executable_with_task_id(self, interpreter, sample_user_tasks):
        """Test that complete with task ID is executable."""
        response = {
            "action": "complete",
            "confidence": 0.95,
            "task_id": 1,
            "needs_clarification": False,
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message="Complete task 1",
                user_id=uuid4(),
                user_tasks=sample_user_tasks,
            )

            assert result.is_executable is True

    @pytest.mark.asyncio
    async def test_complete_not_executable_without_task_id(self, interpreter):
        """Test that complete without task ID is not executable."""
        response = {
            "action": "complete",
            "confidence": 0.5,
            "task_id": None,
            "needs_clarification": True,
            "clarification_question": "Which task?",
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message="complete something",
                user_id=uuid4(),
            )

            assert result.is_executable is False


class TestCompleteIntentVariations:
    """Test various natural language patterns for complete intent."""

    @pytest.fixture
    def base_complete_response(self):
        """Base response for complete variations."""
        return {
            "action": "complete",
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
        "Mark task 1 as done",
        "Complete task 1",
        "I finished task 1",
        "Done with task 1",
        "Task 1 is complete",
        "I've completed task 1",
        "Check off task 1",
        "Tick off task 1",
    ])
    async def test_various_complete_phrases(
        self, interpreter, base_complete_response, sample_tasks, message
    ):
        """Test that various complete phrases are recognized."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = base_complete_response

            result = await interpreter.interpret(
                user_message=message,
                user_id=uuid4(),
                user_tasks=sample_tasks,
            )

            assert result.action == CommandAction.COMPLETE


class TestCompleteTaskMatching:
    """Tests for task matching in complete commands."""

    @pytest.fixture
    def interpreter(self):
        """Create interpreter for matching tests."""
        config = AIConfig(openai_api_key="test-key")
        return AIInterpreter(config=config)

    def test_find_matching_tasks_single_match(self, interpreter):
        """Test finding a single matching task."""
        tasks = [
            {"id": str(uuid4()), "title": "Buy groceries"},
            {"id": str(uuid4()), "title": "Call mom"},
        ]

        matches = interpreter._find_matching_tasks("groceries", tasks)

        assert len(matches) == 1

    def test_find_matching_tasks_multiple_matches(self, interpreter):
        """Test finding multiple matching tasks."""
        tasks = [
            {"id": str(uuid4()), "title": "Buy groceries"},
            {"id": str(uuid4()), "title": "Groceries for party"},
        ]

        matches = interpreter._find_matching_tasks("groceries", tasks)

        assert len(matches) == 2

    def test_find_matching_tasks_no_match(self, interpreter):
        """Test no matching tasks."""
        tasks = [
            {"id": str(uuid4()), "title": "Buy groceries"},
            {"id": str(uuid4()), "title": "Call mom"},
        ]

        matches = interpreter._find_matching_tasks("dentist", tasks)

        assert len(matches) == 0

    def test_find_matching_tasks_case_insensitive(self, interpreter):
        """Test case-insensitive matching."""
        tasks = [
            {"id": str(uuid4()), "title": "Buy Groceries"},
        ]

        matches = interpreter._find_matching_tasks("GROCERIES", tasks)

        assert len(matches) == 1


class TestCLICommandGenerationComplete:
    """Tests for CLI command generation for complete action."""

    @pytest.fixture
    def interpreter(self):
        """Create interpreter for CLI tests."""
        config = AIConfig(openai_api_key="test-key")
        return AIInterpreter(config=config)

    def test_build_complete_cli_with_id(self, interpreter):
        """Test building complete CLI command with task ID."""
        task_id = uuid4()
        result = interpreter._build_cli_command(
            action=CommandAction.COMPLETE,
            title=None,
            task_id=task_id,
            due_date=None,
            status_filter=None,
        )

        assert f"bonsai complete {task_id}" == result

    def test_build_complete_cli_without_id(self, interpreter):
        """Test building complete CLI command without task ID."""
        result = interpreter._build_cli_command(
            action=CommandAction.COMPLETE,
            title=None,
            task_id=None,
            due_date=None,
            status_filter=None,
        )

        assert "bonsai complete <task_id>" == result


class TestMultipleTaskMatchHandling:
    """Tests for handling multiple task matches."""

    @pytest.mark.asyncio
    async def test_multiple_matches_triggers_clarification(self, interpreter):
        """Test that multiple task matches trigger clarification."""
        tasks = [
            {"id": str(uuid4()), "title": "Buy groceries"},
            {"id": str(uuid4()), "title": "Groceries for party"},
        ]

        response = {
            "action": "complete",
            "confidence": 0.85,
            "task_reference": "groceries",
            "needs_clarification": False,
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message="I finished the groceries",
                user_id=uuid4(),
                user_tasks=tasks,
            )

            # Should have multiple matches and need clarification
            assert len(result.multiple_matches) == 2
            assert result.clarification_needed is not None
            assert "specify" in result.clarification_needed.lower() or "which" in result.clarification_needed.lower()


@pytest.fixture
def interpreter():
    """Create interpreter with test config."""
    config = AIConfig(
        openai_api_key="test-key",
        ai_timeout_seconds=5.0,
    )
    return AIInterpreter(config=config)
