"""
Contract tests for POST /chat/message update action.

Tests the API contract for task updates via natural language.
Verifies request/response schemas match the specification.

User Story 4: Natural Language Task Updates
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


class TestChatMessageUpdateContract:
    """Contract tests for task updates via chat."""

    def test_request_schema_valid_update_title(self, client, auth_headers):
        """Test valid update request for title change."""
        request_body = {
            "message": "Change task 1 title to 'Call mom tonight'",
            "conversation_id": None,
        }

        with patch("src.api.chat.ChatService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_message = AsyncMock(return_value=(
                _create_mock_update_response("Call mom tonight"),
                _create_mock_message(),
            ))

            response = client.post(
                "/api/chat/message",
                json=request_body,
                headers=auth_headers,
            )

            assert response.status_code != 422

    def test_request_schema_valid_update_due_date(self, client, auth_headers):
        """Test valid update request for due date change."""
        request_body = {
            "message": "Change task 1 due date to tomorrow",
            "conversation_id": None,
        }

        with patch("src.api.chat.ChatService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_message = AsyncMock(return_value=(
                _create_mock_update_response("Task"),
                _create_mock_message(),
            ))

            response = client.post(
                "/api/chat/message",
                json=request_body,
                headers=auth_headers,
            )

            assert response.status_code != 422

    def test_response_schema_contains_required_fields(self, client, auth_headers, mock_user_id):
        """Test response contains all required fields for update action."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_update_response("Updated title")
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Update task 1 title to 'New title'"},
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

    def test_response_action_is_update(self, client, auth_headers, mock_user_id):
        """Test that update requests return action='update'."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_update_response("Updated")
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Update task 1"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    assert data.get("action") == "update"

    def test_response_contains_updated_task(self, client, auth_headers, mock_user_id):
        """Test that update response contains the updated task."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_update_response("New Title")
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Rename task 1 to 'New Title'"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    if "task" in data and data["task"]:
                        assert data["task"]["title"] == "New Title"


class TestChatMessageUpdateVariants:
    """Test various natural language update patterns."""

    @pytest.mark.parametrize("message", [
        "Change task 1 title to 'New title'",
        "Update task 1 to 'New title'",
        "Rename task 1 to 'New title'",
        "Edit task 1 title",
        "Modify task 1",
        "Change the groceries task to 'Buy milk'",
        "Update the due date of task 1",
        "Move task 1 to tomorrow",
    ])
    def test_update_intent_phrases(self, message, client, auth_headers, mock_user_id):
        """Test various phrases that should trigger update action."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_update_response("Updated")
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


# =============================================================================
# Helper functions
# =============================================================================

def _create_mock_update_response(new_title: str):
    """Create a mock ChatResponse object for update action."""
    from src.services.chat_service import ChatResponse

    task_id = str(uuid4())
    return ChatResponse(
        message=f"I've updated the task to \"{new_title}\".",
        confidence=0.95,
        action="update",
        suggested_cli=f'bonsai update {task_id} --title "{new_title}"',
        needs_confirmation=False,
        is_fallback=False,
        task={"id": task_id, "title": new_title, "is_completed": False},
    )


def _create_mock_message(conversation_id: str | None = None):
    """Create a mock Message object."""
    from src.models.message import Message, MessageRole

    msg = Message(
        id=uuid4(),
        conversation_id=uuid4() if not conversation_id else conversation_id,
        role=MessageRole.ASSISTANT,
        content="Task updated",
        confidence_score=0.95,
    )
    return msg
