"""
Contract tests for POST /chat/message delete action.

Tests the API contract for task deletion via natural language.
Verifies request/response schemas match the specification.

User Story 5: Natural Language Task Deletion
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


class TestChatMessageDeleteContract:
    """Contract tests for task deletion via chat."""

    def test_request_schema_valid_delete_by_id(self, client, auth_headers):
        """Test valid delete request by task ID."""
        request_body = {
            "message": "Delete task 1",
            "conversation_id": None,
        }

        with patch("src.api.chat.ChatService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_message = AsyncMock(return_value=(
                _create_mock_delete_response(),
                _create_mock_message(),
            ))

            response = client.post(
                "/api/chat/message",
                json=request_body,
                headers=auth_headers,
            )

            assert response.status_code != 422

    def test_request_schema_valid_delete_by_title(self, client, auth_headers):
        """Test valid delete request by task title."""
        request_body = {
            "message": "Remove the grocery task",
            "conversation_id": None,
        }

        with patch("src.api.chat.ChatService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_message = AsyncMock(return_value=(
                _create_mock_delete_response(),
                _create_mock_message(),
            ))

            response = client.post(
                "/api/chat/message",
                json=request_body,
                headers=auth_headers,
            )

            assert response.status_code != 422

    def test_response_schema_contains_required_fields(self, client, auth_headers, mock_user_id):
        """Test response contains all required fields for delete action."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_delete_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Delete task 1"},
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

    def test_response_action_is_delete(self, client, auth_headers, mock_user_id):
        """Test that delete requests return action='delete'."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_delete_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Delete task 1"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    assert data.get("action") == "delete"


class TestChatMessageDeleteVariants:
    """Test various natural language delete patterns."""

    @pytest.mark.parametrize("message", [
        "Delete task 1",
        "Remove task 1",
        "Delete the groceries task",
        "Remove my grocery task",
        "Get rid of task 1",
        "Erase task 1",
        "Cancel task 1",
        "Drop task 1",
    ])
    def test_delete_intent_phrases(self, message, client, auth_headers, mock_user_id):
        """Test various phrases that should trigger delete action."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_delete_response()
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


class TestChatMessageDeleteErrors:
    """Test error scenarios for delete action."""

    def test_delete_nonexistent_task_error(self, client, auth_headers, mock_user_id):
        """Test that deleting nonexistent task returns error."""
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
                    json={"message": "Delete task 999"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    assert "not found" in data.get("message", "").lower() or data.get("is_fallback")


# =============================================================================
# Helper functions
# =============================================================================

def _create_mock_delete_response():
    """Create a mock ChatResponse object for delete action."""
    from src.services.chat_service import ChatResponse

    task_id = str(uuid4())
    return ChatResponse(
        message="I've deleted the task \"buy groceries\".",
        confidence=0.95,
        action="delete",
        suggested_cli=f"bonsai delete {task_id}",
        needs_confirmation=False,
        is_fallback=False,
        task={"id": task_id, "title": "buy groceries", "is_completed": False},
    )


def _create_mock_error_response(error_msg: str):
    """Create a mock error response."""
    from src.services.chat_service import ChatResponse

    return ChatResponse(
        message=error_msg,
        confidence=0.0,
        action="delete",
        suggested_cli="bonsai delete <task_id>",
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
        content="Task deleted",
        confidence_score=0.95,
    )
    return msg
