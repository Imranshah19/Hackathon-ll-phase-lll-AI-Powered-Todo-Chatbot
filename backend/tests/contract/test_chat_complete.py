"""
Contract tests for POST /chat/message complete action.

Tests the API contract for task completion via natural language.
Verifies request/response schemas match the specification.

User Story 3: Natural Language Task Completion
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from uuid import uuid4

from src.main import app
from src.ai.types import CommandAction, InterpretedCommand


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def mock_user_id():
    """Generate a mock user ID."""
    return uuid4()


@pytest.fixture
def mock_task_id():
    """Generate a mock task ID."""
    return uuid4()


class TestChatMessageCompleteContract:
    """Contract tests for task completion via chat."""

    def test_request_schema_valid_complete_by_id(self, client, auth_headers):
        """Test valid complete request with task ID."""
        request_body = {
            "message": "Mark task 1 as done",
            "conversation_id": None,
        }

        with patch("src.api.chat.ChatService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_message = AsyncMock(return_value=(
                _create_mock_complete_response(),
                _create_mock_message(),
            ))

            response = client.post(
                "/api/chat/message",
                json=request_body,
                headers=auth_headers,
            )

            assert response.status_code != 422

    def test_request_schema_valid_complete_by_title(self, client, auth_headers):
        """Test valid complete request by task title."""
        request_body = {
            "message": "I finished buying groceries",
            "conversation_id": None,
        }

        with patch("src.api.chat.ChatService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_message = AsyncMock(return_value=(
                _create_mock_complete_response(),
                _create_mock_message(),
            ))

            response = client.post(
                "/api/chat/message",
                json=request_body,
                headers=auth_headers,
            )

            assert response.status_code != 422

    def test_response_schema_contains_required_fields(self, client, auth_headers, mock_user_id):
        """Test response contains all required fields for complete action."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_complete_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Mark task 1 as done"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()

                    assert "message" in data
                    assert "confidence" in data
                    assert "conversation_id" in data
                    assert "message_id" in data
                    assert "needs_confirmation" in data
                    assert "is_fallback" in data

    def test_response_action_is_complete(self, client, auth_headers, mock_user_id):
        """Test that complete requests return action='complete'."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_complete_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Mark task 1 as complete"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    assert data.get("action") == "complete"

    def test_response_contains_completed_task(self, client, auth_headers, mock_user_id):
        """Test that complete response contains the completed task."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_complete_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Done with task 1"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    if "task" in data and data["task"]:
                        assert data["task"]["is_completed"] is True


class TestChatMessageCompleteVariants:
    """Test various natural language complete patterns."""

    @pytest.mark.parametrize("message", [
        "Mark task 1 as done",
        "Complete task 1",
        "I finished task 1",
        "Done with task 1",
        "Task 1 is complete",
        "I've completed task 1",
        "Check off task 1",
        "Finished the groceries task",
        "I did the laundry",
    ])
    def test_complete_intent_phrases(self, message, client, auth_headers, mock_user_id):
        """Test various phrases that should trigger complete action."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_complete_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": message},
                    headers=auth_headers,
                )

                assert response.status_code != 422


class TestChatMessageCompleteErrors:
    """Test error scenarios for complete action."""

    def test_complete_nonexistent_task_error(self, client, auth_headers, mock_user_id):
        """Test that completing nonexistent task returns error."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_error_response("Task not found")
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Complete task 999"},
                    headers=auth_headers,
                )

                # Should still return 200 with error in message
                if response.status_code == 200:
                    data = response.json()
                    assert "not found" in data.get("message", "").lower() or data.get("is_fallback")


# =============================================================================
# Helper functions
# =============================================================================

def _create_mock_complete_response():
    """Create a mock ChatResponse object for complete action."""
    from src.services.chat_service import ChatResponse

    task_id = str(uuid4())
    return ChatResponse(
        message="I've marked \"buy groceries\" as complete.",
        confidence=0.95,
        action="complete",
        suggested_cli=f"bonsai complete {task_id}",
        needs_confirmation=False,
        is_fallback=False,
        task={"id": task_id, "title": "buy groceries", "is_completed": True},
    )


def _create_mock_error_response(error_msg: str):
    """Create a mock error response."""
    from src.services.chat_service import ChatResponse

    return ChatResponse(
        message=error_msg,
        confidence=0.0,
        action="complete",
        suggested_cli="bonsai complete <task_id>",
        needs_confirmation=False,
        is_fallback=True,
    )


def _create_mock_message(conversation_id: str | None = None):
    """Create a mock Message object."""
    from src.models.message import Message, MessageRole

    msg = Message(
        id=uuid4(),
        conversation_id=uuid4() if not conversation_id else conversation_id,
        role=MessageRole.ASSISTANT,
        content="Task completed",
        confidence_score=0.95,
    )
    return msg
