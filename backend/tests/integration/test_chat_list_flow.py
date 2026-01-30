"""
Integration tests for list tasks via chat flow.

Tests the complete flow from user message to task listing.

User Story 2: Natural Language Task Listing

Flow tested:
1. User sends "What are my tasks?"
2. AI interprets as LIST action
3. Executor retrieves tasks via task_service
4. Response shows task list
5. Tasks are returned correctly
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool

from src.ai.types import CommandAction, InterpretedCommand, StatusFilter
from src.ai.executor import CommandExecutor, ExecutionResult
from src.services.chat_service import ChatService, ChatResponse
from src.services.conversation_service import ConversationService
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


@pytest.fixture
def in_memory_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    """Create database session."""
    with Session(in_memory_db) as session:
        yield session


@pytest.fixture
def test_user_id():
    """Generate test user ID."""
    return uuid4()


@pytest.fixture
def other_user_id():
    """Generate another user ID for isolation tests."""
    return uuid4()


def _create_test_task(session, user_id, title, is_completed=False):
    """Helper to create a test task."""
    task = Task(
        title=title,
        user_id=user_id,
        is_completed=is_completed,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


class TestExecutorListAction:
    """Integration tests for executor LIST action."""

    def test_execute_list_returns_all_tasks(self, session, test_user_id):
        """Test that execute LIST returns all user's tasks."""
        # Create some tasks
        _create_test_task(session, test_user_id, "Task 1")
        _create_test_task(session, test_user_id, "Task 2")
        _create_test_task(session, test_user_id, "Task 3", is_completed=True)

        command = InterpretedCommand(
            original_text="What are my tasks?",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list",
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True
        assert result.action == CommandAction.LIST
        assert result.tasks is not None
        assert len(result.tasks) == 3

    def test_execute_list_pending_only(self, session, test_user_id):
        """Test that LIST with pending filter returns only pending tasks."""
        _create_test_task(session, test_user_id, "Pending 1")
        _create_test_task(session, test_user_id, "Pending 2")
        _create_test_task(session, test_user_id, "Completed", is_completed=True)

        command = InterpretedCommand(
            original_text="Show my pending tasks",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list --pending",
            status_filter=StatusFilter.PENDING,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True
        assert len(result.tasks) == 2
        for task in result.tasks:
            assert task["is_completed"] is False

    def test_execute_list_completed_only(self, session, test_user_id):
        """Test that LIST with completed filter returns only completed tasks."""
        _create_test_task(session, test_user_id, "Pending")
        _create_test_task(session, test_user_id, "Completed 1", is_completed=True)
        _create_test_task(session, test_user_id, "Completed 2", is_completed=True)

        command = InterpretedCommand(
            original_text="Show completed tasks",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list --completed",
            status_filter=StatusFilter.COMPLETED,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True
        assert len(result.tasks) == 2
        for task in result.tasks:
            assert task["is_completed"] is True

    def test_execute_list_empty_returns_empty_array(self, session, test_user_id):
        """Test that LIST with no tasks returns empty array."""
        command = InterpretedCommand(
            original_text="What are my tasks?",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list",
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True
        assert result.tasks is not None
        assert len(result.tasks) == 0

    def test_execute_list_user_isolation(self, session, test_user_id, other_user_id):
        """Test that LIST only returns current user's tasks."""
        # Create tasks for both users
        _create_test_task(session, test_user_id, "My Task 1")
        _create_test_task(session, test_user_id, "My Task 2")
        _create_test_task(session, other_user_id, "Other User Task")

        command = InterpretedCommand(
            original_text="What are my tasks?",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list",
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True
        assert len(result.tasks) == 2
        for task in result.tasks:
            assert "Other User" not in task["title"]

    def test_execute_list_returns_task_details(self, session, test_user_id):
        """Test that LIST returns complete task details."""
        _create_test_task(session, test_user_id, "Test Task")

        command = InterpretedCommand(
            original_text="Show tasks",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list",
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True
        assert len(result.tasks) == 1

        task = result.tasks[0]
        assert "id" in task
        assert "title" in task
        assert "is_completed" in task
        assert task["title"] == "Test Task"


class TestChatServiceListFlow:
    """Integration tests for complete chat list flow."""

    @pytest.mark.asyncio
    async def test_full_list_flow(self, session, test_user_id):
        """Test complete flow: message -> interpret -> execute -> response."""
        # Create some tasks first
        _create_test_task(session, test_user_id, "Task 1")
        _create_test_task(session, test_user_id, "Task 2")

        mock_interpreted = InterpretedCommand(
            original_text="What are my tasks?",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list",
        )

        with patch("src.services.chat_service.get_interpreter") as mock_get_interpreter:
            mock_interpreter = MagicMock()
            mock_interpreter.interpret = AsyncMock(return_value=mock_interpreted)
            mock_get_interpreter.return_value = mock_interpreter

            with patch("src.services.chat_service.get_ai_config") as mock_config:
                mock_config.return_value = MagicMock(
                    has_ai_provider=True,
                    max_conversation_context=10,
                )

                chat_service = ChatService(session, test_user_id)
                response, message = await chat_service.process_message(
                    user_message="What are my tasks?",
                )

                # Verify response
                assert response.action == "list"
                assert response.confidence >= 0.9
                assert response.tasks is not None
                assert len(response.tasks) == 2

    @pytest.mark.asyncio
    async def test_list_flow_with_pending_filter(self, session, test_user_id):
        """Test list flow with pending status filter."""
        _create_test_task(session, test_user_id, "Pending Task")
        _create_test_task(session, test_user_id, "Completed Task", is_completed=True)

        mock_interpreted = InterpretedCommand(
            original_text="Show my pending tasks",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list --pending",
            status_filter=StatusFilter.PENDING,
        )

        with patch("src.services.chat_service.get_interpreter") as mock_get_interpreter:
            mock_interpreter = MagicMock()
            mock_interpreter.interpret = AsyncMock(return_value=mock_interpreted)
            mock_get_interpreter.return_value = mock_interpreter

            with patch("src.services.chat_service.get_ai_config") as mock_config:
                mock_config.return_value = MagicMock(
                    has_ai_provider=True,
                    max_conversation_context=10,
                )

                chat_service = ChatService(session, test_user_id)
                response, _ = await chat_service.process_message(
                    user_message="Show my pending tasks",
                )

                assert response.action == "list"
                assert len(response.tasks) == 1
                assert response.tasks[0]["title"] == "Pending Task"

    @pytest.mark.asyncio
    async def test_list_flow_empty_tasks(self, session, test_user_id):
        """Test list flow when user has no tasks."""
        mock_interpreted = InterpretedCommand(
            original_text="What are my tasks?",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list",
        )

        with patch("src.services.chat_service.get_interpreter") as mock_get_interpreter:
            mock_interpreter = MagicMock()
            mock_interpreter.interpret = AsyncMock(return_value=mock_interpreted)
            mock_get_interpreter.return_value = mock_interpreter

            with patch("src.services.chat_service.get_ai_config") as mock_config:
                mock_config.return_value = MagicMock(
                    has_ai_provider=True,
                    max_conversation_context=10,
                )

                chat_service = ChatService(session, test_user_id)
                response, _ = await chat_service.process_message(
                    user_message="What are my tasks?",
                )

                assert response.action == "list"
                assert response.tasks is not None
                assert len(response.tasks) == 0
                # Response message should indicate no tasks
                assert "no" in response.message.lower() or "don't" in response.message.lower()

    @pytest.mark.asyncio
    async def test_list_flow_stores_conversation(self, session, test_user_id):
        """Test that list flow stores messages in conversation."""
        _create_test_task(session, test_user_id, "Test Task")

        mock_interpreted = InterpretedCommand(
            original_text="Show tasks",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list",
        )

        with patch("src.services.chat_service.get_interpreter") as mock_get_interpreter:
            mock_interpreter = MagicMock()
            mock_interpreter.interpret = AsyncMock(return_value=mock_interpreted)
            mock_get_interpreter.return_value = mock_interpreter

            with patch("src.services.chat_service.get_ai_config") as mock_config:
                mock_config.return_value = MagicMock(
                    has_ai_provider=True,
                    max_conversation_context=10,
                )

                chat_service = ChatService(session, test_user_id)
                response, assistant_message = await chat_service.process_message(
                    user_message="Show tasks",
                )

                # Verify conversation was created
                conv_service = ConversationService(session, test_user_id)
                conversations, _ = conv_service.list_conversations()

                assert len(conversations) >= 1

                # Verify messages were stored
                messages = conv_service.get_conversation_messages(
                    assistant_message.conversation_id
                )

                assert len(messages) >= 2
                user_msgs = [m for m in messages if m.role == MessageRole.USER]
                assistant_msgs = [m for m in messages if m.role == MessageRole.ASSISTANT]

                assert len(user_msgs) >= 1
                assert len(assistant_msgs) >= 1


class TestListResponseFormatting:
    """Tests for list response message formatting."""

    @pytest.mark.asyncio
    async def test_single_task_message_format(self, session, test_user_id):
        """Test response message for single task."""
        _create_test_task(session, test_user_id, "Only Task")

        mock_interpreted = InterpretedCommand(
            original_text="Show tasks",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list",
        )

        with patch("src.services.chat_service.get_interpreter") as mock_get_interpreter:
            mock_interpreter = MagicMock()
            mock_interpreter.interpret = AsyncMock(return_value=mock_interpreted)
            mock_get_interpreter.return_value = mock_interpreter

            with patch("src.services.chat_service.get_ai_config") as mock_config:
                mock_config.return_value = MagicMock(
                    has_ai_provider=True,
                    max_conversation_context=10,
                )

                chat_service = ChatService(session, test_user_id)
                response, _ = await chat_service.process_message(
                    user_message="Show tasks",
                )

                # Message should contain the task or indicate tasks exist
                assert "Only Task" in response.message or "task" in response.message.lower()

    @pytest.mark.asyncio
    async def test_multiple_tasks_message_format(self, session, test_user_id):
        """Test response message for multiple tasks."""
        _create_test_task(session, test_user_id, "Task 1")
        _create_test_task(session, test_user_id, "Task 2")
        _create_test_task(session, test_user_id, "Task 3")

        mock_interpreted = InterpretedCommand(
            original_text="Show tasks",
            action=CommandAction.LIST,
            confidence=0.95,
            suggested_cli="bonsai list",
        )

        with patch("src.services.chat_service.get_interpreter") as mock_get_interpreter:
            mock_interpreter = MagicMock()
            mock_interpreter.interpret = AsyncMock(return_value=mock_interpreted)
            mock_get_interpreter.return_value = mock_interpreter

            with patch("src.services.chat_service.get_ai_config") as mock_config:
                mock_config.return_value = MagicMock(
                    has_ai_provider=True,
                    max_conversation_context=10,
                )

                chat_service = ChatService(session, test_user_id)
                response, _ = await chat_service.process_message(
                    user_message="Show tasks",
                )

                # Message should mention the count
                assert "3" in response.message
