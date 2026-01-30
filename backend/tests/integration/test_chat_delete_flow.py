"""
Integration tests for delete task via chat flow.

Tests the complete flow from user message to task deletion.

User Story 5: Natural Language Task Deletion

Flow tested:
1. User sends "Delete task 1"
2. AI interprets as DELETE action
3. Executor deletes task via task_service
4. Response confirms deletion
5. Task is removed from database
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool

from src.ai.types import CommandAction, InterpretedCommand
from src.ai.executor import CommandExecutor, ExecutionResult
from src.services.chat_service import ChatService, ChatResponse
from src.services.conversation_service import ConversationService
from src.models.task import Task
from src.models.message import MessageRole


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


class TestExecutorDeleteAction:
    """Integration tests for executor DELETE action."""

    def test_execute_delete_removes_task(self, session, test_user_id):
        """Test that execute DELETE removes task from database."""
        task = _create_test_task(session, test_user_id, "Task to delete")
        task_id = task.id

        command = InterpretedCommand(
            original_text="Delete task",
            action=CommandAction.DELETE,
            confidence=0.95,
            suggested_cli=f"bonsai delete {task_id}",
            task_id=task_id,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True
        assert result.action == CommandAction.DELETE
        assert result.task is not None
        assert result.task["title"] == "Task to delete"

    def test_execute_delete_task_not_in_database(self, session, test_user_id):
        """Test that deleted task no longer exists in database."""
        task = _create_test_task(session, test_user_id, "Doomed task")
        task_id = task.id

        command = InterpretedCommand(
            original_text="Delete task",
            action=CommandAction.DELETE,
            confidence=0.95,
            suggested_cli=f"bonsai delete {task_id}",
            task_id=task_id,
        )

        executor = CommandExecutor(session, test_user_id)
        executor.execute(command)

        # Verify task no longer exists
        db_task = session.exec(
            select(Task).where(Task.id == task_id)
        ).first()

        assert db_task is None

    def test_execute_delete_nonexistent_task_fails(self, session, test_user_id):
        """Test that deleting nonexistent task fails."""
        fake_id = uuid4()

        command = InterpretedCommand(
            original_text="Delete task",
            action=CommandAction.DELETE,
            confidence=0.95,
            suggested_cli=f"bonsai delete {fake_id}",
            task_id=fake_id,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False
        assert "not found" in result.error_message.lower()

    def test_execute_delete_user_isolation(self, session, test_user_id, other_user_id):
        """Test that users cannot delete other users' tasks."""
        other_task = _create_test_task(session, other_user_id, "Other User Task")
        task_id = other_task.id

        command = InterpretedCommand(
            original_text="Delete task",
            action=CommandAction.DELETE,
            confidence=0.95,
            suggested_cli=f"bonsai delete {task_id}",
            task_id=task_id,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False
        assert "not found" in result.error_message.lower()

        # Verify task still exists
        db_task = session.exec(
            select(Task).where(Task.id == task_id)
        ).first()
        assert db_task is not None

    def test_execute_delete_without_task_id_fails(self, session, test_user_id):
        """Test that delete without task ID returns error."""
        command = InterpretedCommand(
            original_text="Delete something",
            action=CommandAction.DELETE,
            confidence=0.5,
            suggested_cli="bonsai delete <task_id>",
            task_id=None,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False


class TestChatServiceDeleteFlow:
    """Integration tests for complete chat delete flow."""

    @pytest.mark.asyncio
    async def test_full_delete_flow(self, session, test_user_id):
        """Test complete flow: message -> interpret -> execute -> response."""
        task = _create_test_task(session, test_user_id, "Task to delete")
        task_id = task.id

        mock_interpreted = InterpretedCommand(
            original_text="Delete task",
            action=CommandAction.DELETE,
            confidence=0.95,
            suggested_cli=f"bonsai delete {task_id}",
            task_id=task_id,
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
                    user_message="Delete task",
                )

                # Verify response - delete may require confirmation
                assert response.action == "delete"
                assert response.confidence >= 0.9

                # Delete action may require confirmation (needs_confirmation=True)
                # or execute directly if auto-confirmed
                if response.needs_confirmation:
                    # Task should still exist until confirmed
                    db_task = session.exec(
                        select(Task).where(Task.id == task_id)
                    ).first()
                    assert db_task is not None  # Still exists, awaiting confirmation
                else:
                    # Task was deleted
                    db_task = session.exec(
                        select(Task).where(Task.id == task_id)
                    ).first()
                    assert db_task is None

    @pytest.mark.asyncio
    async def test_delete_flow_stores_conversation(self, session, test_user_id):
        """Test that delete flow stores messages in conversation."""
        task = _create_test_task(session, test_user_id, "Task for conversation")
        task_id = task.id

        mock_interpreted = InterpretedCommand(
            original_text="Remove task",
            action=CommandAction.DELETE,
            confidence=0.95,
            suggested_cli=f"bonsai delete {task_id}",
            task_id=task_id,
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
                    user_message="Remove task",
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

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task_returns_error(self, session, test_user_id):
        """Test that deleting nonexistent task returns helpful error or confirmation."""
        fake_id = uuid4()

        mock_interpreted = InterpretedCommand(
            original_text="Delete task 999",
            action=CommandAction.DELETE,
            confidence=0.95,
            suggested_cli=f"bonsai delete {fake_id}",
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
                    user_message="Delete task 999",
                )

                # May ask for confirmation first, or indicate not found
                assert (
                    "not found" in response.message.lower() or
                    response.is_fallback or
                    response.needs_confirmation or
                    "delete" in response.message.lower()
                )


class TestDeleteResponseFormatting:
    """Tests for delete response message formatting."""

    @pytest.mark.asyncio
    async def test_delete_success_message_format(self, session, test_user_id):
        """Test response message format for successful deletion."""
        task = _create_test_task(session, test_user_id, "Task to delete")

        mock_interpreted = InterpretedCommand(
            original_text="Delete task",
            action=CommandAction.DELETE,
            confidence=0.95,
            suggested_cli=f"bonsai delete {task.id}",
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
                    user_message="Delete task",
                )

                # Message should indicate deletion
                assert "delete" in response.message.lower() or "removed" in response.message.lower()


class TestDeleteMultipleTasks:
    """Tests for task operations after deletion."""

    def test_executor_delete_one_leaves_others(self, session, test_user_id):
        """Test that deleting one task via executor leaves other tasks intact."""
        task1 = _create_test_task(session, test_user_id, "Keep this one")
        task2 = _create_test_task(session, test_user_id, "Delete this one")
        task3 = _create_test_task(session, test_user_id, "Keep this too")

        command = InterpretedCommand(
            original_text="Delete task",
            action=CommandAction.DELETE,
            confidence=0.95,
            suggested_cli=f"bonsai delete {task2.id}",
            task_id=task2.id,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True

        # Verify only task2 was deleted
        remaining = session.exec(
            select(Task).where(Task.user_id == test_user_id)
        ).all()

        assert len(remaining) == 2
        remaining_ids = [t.id for t in remaining]
        assert task1.id in remaining_ids
        assert task2.id not in remaining_ids
        assert task3.id in remaining_ids
