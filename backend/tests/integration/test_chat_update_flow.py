"""
Integration tests for update task via chat flow.

Tests the complete flow from user message to task update.

User Story 4: Natural Language Task Updates

Flow tested:
1. User sends "Change task 1 title to 'Call mom tonight'"
2. AI interprets as UPDATE action
3. Executor updates task via task_service
4. Response confirms update
5. Task changes are persisted in database
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import date, timedelta

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


class TestExecutorUpdateAction:
    """Integration tests for executor UPDATE action."""

    def test_execute_update_title(self, session, test_user_id):
        """Test that execute UPDATE changes task title."""
        task = _create_test_task(session, test_user_id, "Old Title")
        original_title = task.title

        command = InterpretedCommand(
            original_text="Update task title",
            action=CommandAction.UPDATE,
            confidence=0.95,
            suggested_cli=f'bonsai update {task.id} --title "New Title"',
            task_id=task.id,
            title="New Title",
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is True
        assert result.action == CommandAction.UPDATE
        assert result.task is not None
        assert result.task["title"] == "New Title"
        assert result.data["old_title"] == original_title

    def test_execute_update_persists_to_database(self, session, test_user_id):
        """Test that update persists to database."""
        task = _create_test_task(session, test_user_id, "Original")

        command = InterpretedCommand(
            original_text="Update task",
            action=CommandAction.UPDATE,
            confidence=0.95,
            suggested_cli=f'bonsai update {task.id} --title "Updated"',
            task_id=task.id,
            title="Updated",
        )

        executor = CommandExecutor(session, test_user_id)
        executor.execute(command)

        # Verify in database
        db_task = session.exec(
            select(Task).where(Task.id == task.id)
        ).first()

        assert db_task.title == "Updated"

    def test_execute_update_nonexistent_task_fails(self, session, test_user_id):
        """Test that updating nonexistent task fails."""
        fake_id = uuid4()

        command = InterpretedCommand(
            original_text="Update task",
            action=CommandAction.UPDATE,
            confidence=0.95,
            suggested_cli=f'bonsai update {fake_id} --title "New"',
            task_id=fake_id,
            title="New Title",
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False
        assert "not found" in result.error_message.lower()

    def test_execute_update_user_isolation(self, session, test_user_id, other_user_id):
        """Test that users cannot update other users' tasks."""
        other_task = _create_test_task(session, other_user_id, "Other User Task")

        command = InterpretedCommand(
            original_text="Update task",
            action=CommandAction.UPDATE,
            confidence=0.95,
            suggested_cli=f'bonsai update {other_task.id} --title "Hacked"',
            task_id=other_task.id,
            title="Hacked",
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False
        assert "not found" in result.error_message.lower()

        # Verify task unchanged
        db_task = session.exec(
            select(Task).where(Task.id == other_task.id)
        ).first()
        assert db_task.title == "Other User Task"

    def test_execute_update_without_changes_fails(self, session, test_user_id):
        """Test that update without any changes returns error."""
        task = _create_test_task(session, test_user_id, "Task")

        command = InterpretedCommand(
            original_text="Update task",
            action=CommandAction.UPDATE,
            confidence=0.95,
            suggested_cli=f"bonsai update {task.id}",
            task_id=task.id,
            title=None,
            due_date=None,
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False
        assert "specify" in result.error_message.lower() or "update" in result.error_message.lower()

    def test_execute_update_without_task_id_fails(self, session, test_user_id):
        """Test that update without task ID returns error."""
        command = InterpretedCommand(
            original_text="Update something",
            action=CommandAction.UPDATE,
            confidence=0.5,
            suggested_cli="bonsai update <task_id>",
            task_id=None,
            title="New Title",
        )

        executor = CommandExecutor(session, test_user_id)
        result = executor.execute(command)

        assert result.success is False


class TestChatServiceUpdateFlow:
    """Integration tests for complete chat update flow."""

    @pytest.mark.asyncio
    async def test_full_update_flow(self, session, test_user_id):
        """Test complete flow: message -> interpret -> execute -> response."""
        task = _create_test_task(session, test_user_id, "Original Title")

        mock_interpreted = InterpretedCommand(
            original_text="Change task title",
            action=CommandAction.UPDATE,
            confidence=0.95,
            suggested_cli=f'bonsai update {task.id} --title "New Title"',
            task_id=task.id,
            title="New Title",
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
                    user_message="Change task title to 'New Title'",
                )

                # Verify response
                assert response.action == "update"
                assert response.confidence >= 0.9
                assert response.task is not None
                assert response.task["title"] == "New Title"

                # Verify task was updated in database
                db_task = session.exec(
                    select(Task).where(Task.id == task.id)
                ).first()

                assert db_task.title == "New Title"

    @pytest.mark.asyncio
    async def test_update_flow_stores_conversation(self, session, test_user_id):
        """Test that update flow stores messages in conversation."""
        task = _create_test_task(session, test_user_id, "Task to update")

        mock_interpreted = InterpretedCommand(
            original_text="Rename task",
            action=CommandAction.UPDATE,
            confidence=0.95,
            suggested_cli=f'bonsai update {task.id} --title "Renamed"',
            task_id=task.id,
            title="Renamed",
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
                    user_message="Rename task",
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
    async def test_update_nonexistent_task_returns_error(self, session, test_user_id):
        """Test that updating nonexistent task returns helpful error."""
        fake_id = uuid4()

        mock_interpreted = InterpretedCommand(
            original_text="Update task 999",
            action=CommandAction.UPDATE,
            confidence=0.95,
            suggested_cli=f'bonsai update {fake_id} --title "New"',
            task_id=fake_id,
            title="New Title",
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
                    user_message="Update task 999",
                )

                assert "not found" in response.message.lower() or response.is_fallback


class TestUpdateIncompleteRequest:
    """Tests for handling incomplete update requests."""

    @pytest.mark.asyncio
    async def test_incomplete_update_requests_clarification(self, session, test_user_id):
        """Test that incomplete update requests clarification."""
        task = _create_test_task(session, test_user_id, "Task")

        mock_interpreted = InterpretedCommand(
            original_text="Update task 1",
            action=CommandAction.UPDATE,
            confidence=0.6,
            suggested_cli=f"bonsai update {task.id}",
            task_id=task.id,
            title=None,
            due_date=None,
            clarification_needed="What would you like to update? (title or due date)",
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
                    user_message="Update task 1",
                )

                # Should request clarification or indicate what's missing
                assert response.needs_confirmation or response.is_fallback or "what" in response.message.lower()


class TestUpdateResponseFormatting:
    """Tests for update response message formatting."""

    @pytest.mark.asyncio
    async def test_update_success_message_format(self, session, test_user_id):
        """Test response message format for successful update."""
        task = _create_test_task(session, test_user_id, "Old Title")

        mock_interpreted = InterpretedCommand(
            original_text="Rename task",
            action=CommandAction.UPDATE,
            confidence=0.95,
            suggested_cli=f'bonsai update {task.id} --title "New Title"',
            task_id=task.id,
            title="New Title",
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
                    user_message="Rename task",
                )

                # Message should indicate update
                assert "update" in response.message.lower() or "change" in response.message.lower() or "renamed" in response.message.lower()
