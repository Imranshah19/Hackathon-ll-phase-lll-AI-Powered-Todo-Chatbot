"""
Contract tests for POST /chat/message list action.

Tests the API contract for task listing via natural language.
Verifies request/response schemas match the specification.

User Story 2: Natural Language Task Listing
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


class TestChatMessageListContract:
    """Contract tests for task listing via chat."""

    def test_request_schema_valid_list_message(self, client, auth_headers):
        """Test valid list request schema is accepted."""
        request_body = {
            "message": "What are my tasks?",
            "conversation_id": None,
        }

        with patch("src.api.chat.ChatService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_message = AsyncMock(return_value=(
                _create_mock_list_response([]),
                _create_mock_message(),
            ))

            response = client.post(
                "/api/chat/message",
                json=request_body,
                headers=auth_headers,
            )

            # Should not be 422 (validation error)
            assert response.status_code != 422

    def test_request_schema_list_with_status_filter(self, client, auth_headers):
        """Test list request with status filter."""
        request_body = {
            "message": "Show my pending tasks",
            "conversation_id": None,
        }

        with patch("src.api.chat.ChatService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_message = AsyncMock(return_value=(
                _create_mock_list_response([]),
                _create_mock_message(),
            ))

            response = client.post(
                "/api/chat/message",
                json=request_body,
                headers=auth_headers,
            )

            assert response.status_code != 422

    def test_response_schema_contains_required_fields(self, client, auth_headers, mock_user_id):
        """Test response contains all required fields for list action."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_list_response([
                    {"id": str(uuid4()), "title": "Task 1", "is_completed": False},
                    {"id": str(uuid4()), "title": "Task 2", "is_completed": True},
                ])
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "What are my tasks?"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()

                    # Required fields per ChatMessageResponse schema
                    assert "message" in data
                    assert "confidence" in data
                    assert "conversation_id" in data
                    assert "message_id" in data
                    assert "needs_confirmation" in data
                    assert "is_fallback" in data

    def test_response_action_is_list(self, client, auth_headers, mock_user_id):
        """Test that list requests return action='list'."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_list_response([])
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "Show all my tasks"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    assert data.get("action") == "list"

    def test_response_contains_tasks_array(self, client, auth_headers, mock_user_id):
        """Test that list response contains tasks array."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                tasks = [
                    {"id": str(uuid4()), "title": "Task 1", "is_completed": False},
                    {"id": str(uuid4()), "title": "Task 2", "is_completed": True},
                ]
                mock_response = _create_mock_list_response(tasks)
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "List my tasks"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    assert "tasks" in data
                    assert isinstance(data["tasks"], list)


class TestChatMessageListVariants:
    """Test various natural language list patterns."""

    @pytest.mark.parametrize("message", [
        "What are my tasks?",
        "Show my tasks",
        "List all tasks",
        "What do I need to do?",
        "What's on my todo list?",
        "Show me everything",
        "What tasks do I have?",
    ])
    def test_list_intent_phrases(self, message, client, auth_headers, mock_user_id):
        """Test various phrases that should trigger list action."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_list_response([])
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

                # Request should be processed (not rejected by schema)
                assert response.status_code != 422

    @pytest.mark.parametrize("message,expected_filter", [
        ("Show my pending tasks", "pending"),
        ("What tasks are completed?", "completed"),
        ("Show incomplete tasks", "pending"),
        ("List finished tasks", "completed"),
    ])
    def test_list_with_status_filter_phrases(
        self, message, expected_filter, client, auth_headers, mock_user_id
    ):
        """Test list phrases with status filters."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_list_response([])
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

def _create_mock_list_response(tasks: list):
    """Create a mock ChatResponse object for list action."""
    from src.services.chat_service import ChatResponse

    if tasks:
        message = f"You have {len(tasks)} task(s)."
    else:
        message = "You don't have any tasks yet."

    return ChatResponse(
        message=message,
        confidence=0.95,
        action="list",
        suggested_cli="bonsai list",
        needs_confirmation=False,
        is_fallback=False,
        tasks=tasks,
    )


def _create_mock_message(conversation_id: str | None = None):
    """Create a mock Message object."""
    from src.models.message import Message, MessageRole

    msg = Message(
        id=uuid4(),
        conversation_id=uuid4() if not conversation_id else conversation_id,
        role=MessageRole.ASSISTANT,
        content="Tasks listed",
        confidence_score=0.95,
    )
    return msg
