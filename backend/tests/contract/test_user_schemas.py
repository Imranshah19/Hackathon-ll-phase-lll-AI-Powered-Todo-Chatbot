"""
Contract tests for User schemas.

Tests:
- T015: Validate User schemas match OpenAPI specification
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4


@pytest.mark.contract
class TestUserSchemaContract:
    """Contract tests ensuring User schemas match API specification."""

    def test_user_public_has_required_fields(self) -> None:
        """UserPublic must have: id, email, created_at, updated_at."""
        from src.models.user import UserPublic

        # Get model fields
        fields = UserPublic.model_fields

        required_fields = ["id", "email", "created_at", "updated_at"]
        for field in required_fields:
            assert field in fields, f"UserPublic missing required field: {field}"

    def test_user_public_excludes_sensitive_fields(self) -> None:
        """UserPublic must NOT have: password, password_hash."""
        from src.models.user import UserPublic

        fields = UserPublic.model_fields

        sensitive_fields = ["password", "password_hash"]
        for field in sensitive_fields:
            assert field not in fields, f"UserPublic has sensitive field: {field}"

    def test_user_create_has_required_fields(self) -> None:
        """UserCreate must have: email, password."""
        from src.models.user import UserCreate

        fields = UserCreate.model_fields

        required_fields = ["email", "password"]
        for field in required_fields:
            assert field in fields, f"UserCreate missing required field: {field}"

    def test_user_create_password_not_hash(self) -> None:
        """UserCreate must accept 'password' not 'password_hash'."""
        from src.models.user import UserCreate

        fields = UserCreate.model_fields

        assert "password" in fields, "UserCreate should have 'password' field"
        assert "password_hash" not in fields, "UserCreate should NOT have 'password_hash'"

    def test_user_public_json_serialization(self) -> None:
        """UserPublic should serialize to JSON matching OpenAPI spec."""
        from src.models.user import UserPublic

        user_public = UserPublic(
            id=uuid4(),
            email="test@example.com",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        json_data = user_public.model_dump(mode="json")

        # Check JSON structure matches OpenAPI
        assert "id" in json_data
        assert "email" in json_data
        assert "created_at" in json_data
        assert "updated_at" in json_data
        assert "password_hash" not in json_data

        # id should be string (UUID serialized)
        assert isinstance(json_data["id"], str)
        # email should be string
        assert isinstance(json_data["email"], str)
        # timestamps should be ISO format strings
        assert isinstance(json_data["created_at"], str)
        assert isinstance(json_data["updated_at"], str)

    def test_user_create_accepts_valid_input(self) -> None:
        """UserCreate should accept valid JSON input."""
        from src.models.user import UserCreate

        input_data = {
            "email": "user@example.com",
            "password": "securepass123"
        }

        user_create = UserCreate.model_validate(input_data)

        assert user_create.email == input_data["email"]
        assert user_create.password == input_data["password"]

    def test_user_id_is_uuid_format(self) -> None:
        """User.id should be UUID v4 format."""
        from src.models.user import User

        user = User(
            email="test@example.com",
            password_hash="hash"
        )

        # UUID should be version 4
        assert user.id.version == 4

    def test_user_email_format_validation(self) -> None:
        """UserCreate.email should validate email format per RFC 5322."""
        from pydantic import ValidationError
        from src.models.user import UserCreate

        # Invalid emails should be rejected
        invalid_emails = [
            "not-an-email",
            "missing@",
            "@missing-local",
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError):
                UserCreate(email=invalid_email, password="password123")
