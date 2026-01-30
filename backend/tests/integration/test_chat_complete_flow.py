"""
Integration tests for complete task via chat flow.

Tests the complete flow from user message to task completion.

User Story 3: Natural Language Task Completion

Flow tested:
1. User sends "Mark task 1 as done"
2. AI interprets as COMPLETE action
3. Executor marks task as completed via task_service
4. Response confirms completion
5. Task status is updated in database
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4, UUID

from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool

from src.ai.types import CommandAction, InterpretedCommand
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


def _create_test_task(session, user_id, title, is_completed=False) -> Task:
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


class TestExecutorCompleteAction:
    """Integration tests for executor COMPLETE action."""

    def test_execute_complete_marks_task_done(self, session, test_user_id):
        """Test that execute COMPLETE marks task as completed."""
        task = _create_test_task(session, test_user_id, "Test Task")
        assert task.is_completed is False

        command = InterpretedCommand(
            original_text="Mark task as done",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {task.id}",
            task_id=task.id,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True
        assert result.action == CommandAction.COMPLETE
        assert result.task is not None
        assert result.task["is_completed"] is True

    def test_execute_complete_persists_to_database(self, session, test_user_id):
        """Test that completion status persists to database."""
        task = _create_test_task(session, test_user_id, "Persist Test")

        command = InterpretedCommand(
            original_text="Complete task",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {task.id}",
            task_id=task.id,
        )

        executor = CommandExecutor(session, test_user_id)
        executor.execute(command)

        # Verify in database
        db_task = session.exec(
            select(Task).where(Task.id == task.id)
        ).first()

        assert db_task.is_completed is True

    def test_execute_complete_nonexistent_task_fails(self, session, test_user_id):
        """Test that completing nonexistent task fails."""
        fake_id = uuid4()

        command = InterpretedCommand(
            original_text="Complete task",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {fake_id}",
            task_id=fake_id,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False
        assert "not found" in result.error_message.lower()

    def test_execute_complete_already_completed_task(self, session, test_user_id):
        """Test completing an already completed task."""
        task = _create_test_task(session, test_user_id, "Already Done", is_completed=True)

        command = InterpretedCommand(
            original_text="Complete task",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {task.id}",
            task_id=task.id,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        # Should still succeed but indicate it was already completed
        assert result.success is True
        assert result.data is not None
        assert result.data.get("already_completed") is True

    def test_execute_complete_user_isolation(self, session, test_user_id, other_user_id):
        """Test that users cannot complete other users' tasks."""
        # Create task for other user
        other_task = _create_test_task(session, other_user_id, "Other User Task")

        command = InterpretedCommand(
            original_text="Complete task",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {other_task.id}",
            task_id=other_task.id,
        )

        # Try to complete as test_user
        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False
        assert "not found" in result.error_message.lower()

    def test_execute_complete_without_task_id_fails(self, session, test_user_id):
        """Test that complete without task ID returns error."""
        command = InterpretedCommand(
            original_text="Complete something",
            action=CommandAction.COMPLETE,
            confidence=0.5,
            suggested_cli="bonsai complete <task_id>",
            task_id=None,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False


class TestChatServiceCompleteFlow:
    """Integration tests for complete chat flow."""

    @pytest.mark.asyncio
    async def test_full_complete_flow(self, session, test_user_id):
        """Test complete flow: message -> interpret -> execute -> response."""
        task = _create_test_task(session, test_user_id, "Task to complete")

        mock_interpreted = InterpretedCommand(
            original_text="Mark task as done",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {task.id}",
            task_id=task.id,
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
                    user_message="Mark task as done",
                )

                # Verify response
                assert response.action == "complete"
                assert response.confidence >= 0.9
                assert response.task is not None
                assert response.task["is_completed"] is True

                # Verify task was completed in database
                db_task = session.exec(
                    select(Task).where(Task.id == task.id)
                ).first()

                assert db_task.is_completed is True

    @pytest.mark.asyncio
    async def test_complete_flow_stores_conversation(self, session, test_user_id):
        """Test that complete flow stores messages in conversation."""
        task = _create_test_task(session, test_user_id, "Task for conversation")

        mock_interpreted = InterpretedCommand(
            original_text="Done with task",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {task.id}",
            task_id=task.id,
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
                    user_message="Done with task",
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

    @pytest.mark.asyncio
    async def test_complete_nonexistent_task_returns_error(self, session, test_user_id):
        """Test that completing nonexistent task returns helpful error."""
        fake_id = uuid4()

        mock_interpreted = InterpretedCommand(
            original_text="Complete task 999",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {fake_id}",
            task_id=fake_id,
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
                    user_message="Complete task 999",
                )

                # Should indicate failure
                assert "not found" in response.message.lower() or response.is_fallback


class TestCompleteWithTaskReference:
    """Tests for completing tasks by title reference."""

    @pytest.mark.asyncio
    async def test_complete_by_title_reference(self, session, test_user_id):
        """Test completing a task by title reference."""
        task = _create_test_task(session, test_user_id, "Buy groceries")

        mock_interpreted = InterpretedCommand(
            original_text="I finished buying groceries",
            action=CommandAction.COMPLETE,
            confidence=0.88,
            suggested_cli=f"bonsai complete {task.id}",
            task_id=task.id,
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
                    user_message="I finished buying groceries",
                )

                assert response.action == "complete"
                assert response.task["is_completed"] is True

    @pytest.mark.asyncio
    async def test_multiple_matches_requests_clarification(self, session, test_user_id):
        """Test that multiple task matches request clarification."""
        _create_test_task(session, test_user_id, "Buy groceries")
        _create_test_task(session, test_user_id, "Groceries for party")

        # AI returns multiple matches
        mock_interpreted = InterpretedCommand(
            original_text="I finished the groceries",
            action=CommandAction.COMPLETE,
            confidence=0.7,
            suggested_cli="bonsai complete <task_id>",
            task_id=None,
            clarification_needed="Multiple tasks match 'groceries'. Please specify which one.",
            multiple_matches=[uuid4(), uuid4()],
        )

        with patch("src.services.chat_service.get_interpreter") as mock_get_interpreter:
            mock_interpreter = MagicMock()
            mock_interpreter.interpret = AsyncMock(return_value=mock_interpreted)
            mock_get_interpreter.return_value = mock_interpreter

            with patch("src.services.chat_service.get_ai_config") as mock_config:
                mock_config.return_value = MagicMock(
                    has_ai_provider=True,
                    max_conversation_context=10,
                    confidence_threshold_low=0.5,
                    confidence_threshold_high=0.8,
                )

                chat_service = ChatService(session, test_user_id)
                response, _ = await chat_service.process_message(
                    user_message="I finished the groceries",
                )

                # Should request clarification
                assert response.needs_confirmation or response.is_fallback or "specify" in response.message.lower()


class TestCompleteResponseFormatting:
    """Tests for complete response message formatting."""

    @pytest.mark.asyncio
    async def test_complete_success_message_format(self, session, test_user_id):
        """Test response message format for successful completion."""
        task = _create_test_task(session, test_user_id, "Important task")

        mock_interpreted = InterpretedCommand(
            original_text="Done with task",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {task.id}",
            task_id=task.id,
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
                    user_message="Done with task",
                )

                # Message should indicate completion
                assert "complete" in response.message.lower() or "done" in response.message.lower() or "marked" in response.message.lower()

    @pytest.mark.asyncio
    async def test_complete_already_done_message(self, session, test_user_id):
        """Test response message when task was already completed."""
        task = _create_test_task(session, test_user_id, "Already done task", is_completed=True)

        mock_interpreted = InterpretedCommand(
            original_text="Complete task",
            action=CommandAction.COMPLETE,
            confidence=0.95,
            suggested_cli=f"bonsai complete {task.id}",
            task_id=task.id,
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
                    user_message="Complete task",
                )

                # Response should still succeed
                assert response.task["is_completed"] is True
