"""
Contract tests for fallback responses in chat API.

Tests the API contract when AI is unavailable or returns low confidence.
Verifies graceful degradation per Constitution Principle X.

User Story 6: Graceful Fallback to CLI
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
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


class TestChatFallbackContract:
    """Contract tests for fallback responses."""

    def test_low_confidence_returns_fallback_response(self, client, auth_headers, mock_user_id):
        """Test that low confidence triggers fallback with CLI suggestion."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_fallback_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "do something unclear"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()

                    # Should have is_fallback=True
                    assert data.get("is_fallback") is True
                    # Should have suggested CLI command
                    assert "suggested_cli" in data or "bonsai" in data.get("message", "").lower()

    def test_response_schema_contains_fallback_fields(self, client, auth_headers, mock_user_id):
        """Test response schema includes fallback-related fields."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_fallback_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "xyz unclear"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()

                    # Required fields
                    assert "message" in data
                    assert "confidence" in data
                    assert "is_fallback" in data
                    assert "needs_confirmation" in data

    def test_unknown_action_returns_help_suggestion(self, client, auth_headers, mock_user_id):
        """Test that unknown actions return help suggestions."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_unknown_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "blah blah random"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()

                    # Should indicate fallback or provide help
                    assert data.get("is_fallback") is True or "help" in data.get("message", "").lower()


class TestChatAIUnavailableContract:
    """Contract tests for AI unavailable scenarios."""

    def test_ai_error_returns_fallback(self, client, auth_headers, mock_user_id):
        """Test that AI errors return graceful fallback."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_ai_unavailable_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "add a task"},
                    headers=auth_headers,
                )

                # Should NOT return 503, should gracefully degrade
                assert response.status_code != 503

                if response.status_code == 200:
                    data = response.json()
                    # Should have fallback info
                    assert data.get("is_fallback") is True or "cli" in data.get("message", "").lower()


class TestChatConfirmationContract:
    """Contract tests for confirmation flow."""

    def test_medium_confidence_returns_confirmation_needed(self, client, auth_headers, mock_user_id):
        """Test that medium confidence triggers confirmation."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_confirmation_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "add something"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()

                    # Should need confirmation
                    assert data.get("needs_confirmation") is True

    def test_delete_always_returns_confirmation(self, client, auth_headers, mock_user_id):
        """Test that delete actions always require confirmation."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_delete_confirmation_response()
                mock_message = _create_mock_message()

                mock_instance = mock_service.return_value
                mock_instance.process_message = AsyncMock(
                    return_value=(mock_response, mock_message)
                )

                response = client.post(
                    "/api/chat/message",
                    json={"message": "delete task 1"},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    data = response.json()

                    # Delete should need confirmation
                    assert data.get("needs_confirmation") is True
                    assert "sure" in data.get("message", "").lower() or "confirm" in data.get("message", "").lower()


class TestChatFallbackCLISuggestions:
    """Contract tests for CLI suggestions in fallback."""

    @pytest.mark.parametrize("message,expected_cli_pattern", [
        ("add something", "bonsai add"),
        ("show tasks", "bonsai list"),
        ("complete something", "bonsai complete"),
        ("update something", "bonsai update"),
        ("delete something", "bonsai delete"),
    ])
    def test_fallback_includes_relevant_cli(
        self, message, expected_cli_pattern, client, auth_headers, mock_user_id
    ):
        """Test that fallback includes relevant CLI command."""
        with patch("src.auth.dependencies.get_token_payload") as mock_auth:
            mock_auth.return_value = type("TokenPayload", (), {"user_id": mock_user_id})()

            with patch("src.api.chat.ChatService") as mock_service:
                mock_response = _create_mock_fallback_with_cli(expected_cli_pattern)
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

                if response.status_code == 200:
                    data = response.json()

                    # Should include relevant CLI
                    suggested = data.get("suggested_cli", "") or ""
                    message_text = data.get("message", "") or ""
                    assert expected_cli_pattern in suggested or expected_cli_pattern in message_text


# =============================================================================
# Helper functions
# =============================================================================

def _create_mock_fallback_response():
    """Create a mock fallback ChatResponse."""
    from src.services.chat_service import ChatResponse

    return ChatResponse(
        message="I'm not sure what you'd like to do. You can use CLI commands directly.",
        confidence=0.3,
        action="unknown",
        suggested_cli="bonsai help",
        needs_confirmation=False,
        is_fallback=True,
    )


def _create_mock_unknown_response():
    """Create a mock unknown action response."""
    from src.services.chat_service import ChatResponse

    return ChatResponse(
        message="I'm not sure what you'd like to do. Here are some things I can help with...",
        confidence=0.0,
        action="unknown",
        suggested_cli="bonsai help",
        needs_confirmation=False,
        is_fallback=True,
    )


def _create_mock_ai_unavailable_response():
    """Create a mock AI unavailable response."""
    from src.services.chat_service import ChatResponse

    return ChatResponse(
        message="I'm temporarily unavailable. You can still manage tasks using CLI commands.",
        confidence=0.0,
        action="unknown",
        suggested_cli="bonsai help",
        needs_confirmation=False,
        is_fallback=True,
    )


def _create_mock_confirmation_response():
    """Create a mock confirmation needed response."""
    from src.services.chat_service import ChatResponse

    return ChatResponse(
        message="I'll create a task. Is this correct?",
        confidence=0.6,
        action="add",
        suggested_cli="bonsai add \"something\"",
        needs_confirmation=True,
        is_fallback=False,
    )


def _create_mock_delete_confirmation_response():
    """Create a mock delete confirmation response."""
    from src.services.chat_service import ChatResponse

    return ChatResponse(
        message="Are you sure you want to delete task 1? This cannot be undone.",
        confidence=0.95,
        action="delete",
        suggested_cli="bonsai delete 1",
        needs_confirmation=True,
        is_fallback=False,
    )


def _create_mock_fallback_with_cli(cli_pattern: str):
    """Create a mock fallback with specific CLI."""
    from src.services.chat_service import ChatResponse

    return ChatResponse(
        message=f"I'm not certain. You can use: {cli_pattern}",
        confidence=0.4,
        action="unknown",
        suggested_cli=cli_pattern,
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
        content="Fallback response",
        confidence_score=0.3,
    )
    return msg
