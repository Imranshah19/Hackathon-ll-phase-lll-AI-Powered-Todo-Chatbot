"""
Unit tests for LIST intent extraction in AIInterpreter.

Tests the interpretation of natural language task listing commands.

User Story 2: Natural Language Task Listing
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.ai.interpreter import AIInterpreter
from src.ai.types import CommandAction, ConfidenceLevel, StatusFilter
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
def mock_openai_list_all_response():
    """Mock OpenAI response for list all tasks."""
    return {
        "action": "list",
        "confidence": 0.95,
        "status_filter": None,
        "needs_clarification": False,
    }


@pytest.fixture
def mock_openai_list_pending_response():
    """Mock OpenAI response for list pending tasks."""
    return {
        "action": "list",
        "confidence": 0.92,
        "status_filter": "pending",
        "needs_clarification": False,
    }


@pytest.fixture
def mock_openai_list_completed_response():
    """Mock OpenAI response for list completed tasks."""
    return {
        "action": "list",
        "confidence": 0.90,
        "status_filter": "completed",
        "needs_clarification": False,
    }


class TestListIntentExtraction:
    """Tests for LIST action intent extraction."""

    @pytest.mark.asyncio
    async def test_extract_simple_list_intent(self, interpreter, mock_openai_list_all_response):
        """Test extraction of simple list command."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_list_all_response

            result = await interpreter.interpret(
                user_message="What are my tasks?",
                user_id=uuid4(),
            )

            assert result.action == CommandAction.LIST
            assert result.confidence >= 0.8
            assert result.confidence_level == ConfidenceLevel.HIGH

    @pytest.mark.asyncio
    async def test_extract_list_pending_intent(self, interpreter, mock_openai_list_pending_response):
        """Test extraction of list pending tasks command."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_list_pending_response

            result = await interpreter.interpret(
                user_message="Show my pending tasks",
                user_id=uuid4(),
            )

            assert result.action == CommandAction.LIST
            assert result.status_filter == StatusFilter.PENDING
            assert result.confidence >= 0.8

    @pytest.mark.asyncio
    async def test_extract_list_completed_intent(self, interpreter, mock_openai_list_completed_response):
        """Test extraction of list completed tasks command."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_list_completed_response

            result = await interpreter.interpret(
                user_message="What tasks have I completed?",
                user_id=uuid4(),
            )

            assert result.action == CommandAction.LIST
            assert result.status_filter == StatusFilter.COMPLETED
            assert result.confidence >= 0.8

    @pytest.mark.asyncio
    async def test_list_no_status_filter_by_default(self, interpreter, mock_openai_list_all_response):
        """Test that list without filter returns all tasks."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_list_all_response

            result = await interpreter.interpret(
                user_message="Show all my tasks",
                user_id=uuid4(),
            )

            assert result.action == CommandAction.LIST
            assert result.status_filter is None

    @pytest.mark.asyncio
    async def test_suggested_cli_for_list_all(self, interpreter, mock_openai_list_all_response):
        """Test that suggested CLI command is generated correctly for list all."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_list_all_response

            result = await interpreter.interpret(
                user_message="What are my tasks?",
                user_id=uuid4(),
            )

            assert "bonsai list" in result.suggested_cli

    @pytest.mark.asyncio
    async def test_suggested_cli_for_list_pending(self, interpreter, mock_openai_list_pending_response):
        """Test that suggested CLI includes pending flag."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_list_pending_response

            result = await interpreter.interpret(
                user_message="Show my pending tasks",
                user_id=uuid4(),
            )

            assert "bonsai list" in result.suggested_cli
            assert "--pending" in result.suggested_cli

    @pytest.mark.asyncio
    async def test_suggested_cli_for_list_completed(self, interpreter, mock_openai_list_completed_response):
        """Test that suggested CLI includes completed flag."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_list_completed_response

            result = await interpreter.interpret(
                user_message="Show completed tasks",
                user_id=uuid4(),
            )

            assert "bonsai list" in result.suggested_cli
            assert "--completed" in result.suggested_cli

    @pytest.mark.asyncio
    async def test_list_is_always_executable(self, interpreter, mock_openai_list_all_response):
        """Test that list is always executable (no parameters needed)."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_list_all_response

            result = await interpreter.interpret(
                user_message="Show tasks",
                user_id=uuid4(),
            )

            assert result.is_executable is True


class TestListIntentVariations:
    """Test various natural language patterns for list intent."""

    @pytest.fixture
    def base_list_response(self):
        """Base response for list variations."""
        return {
            "action": "list",
            "confidence": 0.9,
            "needs_clarification": False,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message", [
        "What are my tasks?",
        "Show my tasks",
        "List all tasks",
        "What do I need to do?",
        "What's on my todo list?",
        "Show me everything",
        "What tasks do I have?",
        "Display my tasks",
        "Give me my task list",
    ])
    async def test_various_list_phrases(self, interpreter, base_list_response, message):
        """Test that various list phrases are recognized."""
        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = base_list_response

            result = await interpreter.interpret(
                user_message=message,
                user_id=uuid4(),
            )

            assert result.action == CommandAction.LIST

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_filter", [
        ("Show my pending tasks", StatusFilter.PENDING),
        ("What tasks are completed?", StatusFilter.COMPLETED),
        ("Show incomplete tasks", StatusFilter.PENDING),
        ("List finished tasks", StatusFilter.COMPLETED),
        ("What's left to do?", StatusFilter.PENDING),
        ("What have I done?", StatusFilter.COMPLETED),
    ])
    async def test_list_with_status_filter_phrases(
        self, interpreter, message, expected_filter
    ):
        """Test list phrases with status filters."""
        response = {
            "action": "list",
            "confidence": 0.9,
            "status_filter": expected_filter.value,
            "needs_clarification": False,
        }

        with patch.object(interpreter, "_call_openai", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = response

            result = await interpreter.interpret(
                user_message=message,
                user_id=uuid4(),
            )

            assert result.action == CommandAction.LIST
            assert result.status_filter == expected_filter


class TestCLICommandGenerationList:
    """Tests for CLI command generation for list action."""

    @pytest.fixture
    def interpreter(self):
        """Create interpreter for CLI tests."""
        config = AIConfig(openai_api_key="test-key")
        return AIInterpreter(config=config)

    def test_build_list_cli_all(self, interpreter):
        """Test building list CLI command for all tasks."""
        result = interpreter._build_cli_command(
            action=CommandAction.LIST,
            title=None,
            task_id=None,
            due_date=None,
            status_filter=None,
        )

        assert result == "bonsai list"

    def test_build_list_cli_pending(self, interpreter):
        """Test building list CLI command for pending tasks."""
        result = interpreter._build_cli_command(
            action=CommandAction.LIST,
            title=None,
            task_id=None,
            due_date=None,
            status_filter=StatusFilter.PENDING,
        )

        assert result == "bonsai list --pending"

    def test_build_list_cli_completed(self, interpreter):
        """Test building list CLI command for completed tasks."""
        result = interpreter._build_cli_command(
            action=CommandAction.LIST,
            title=None,
            task_id=None,
            due_date=None,
            status_filter=StatusFilter.COMPLETED,
        )

        assert result == "bonsai list --completed"
