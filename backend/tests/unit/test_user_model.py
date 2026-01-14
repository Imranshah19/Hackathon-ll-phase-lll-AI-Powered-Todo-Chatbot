"""
Unit tests for User model and schemas.

Tests:
- T011: User model creation (UUID generation, timestamps)
- T012: UserCreate validation (email format, password min length)
- T013: UserPublic schema (password_hash excluded)
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID


# =============================================================================
# T011: User Model Creation Tests
# =============================================================================

@pytest.mark.unit
class TestUserModelCreation:
    """Test User model creation with UUID and timestamps."""

    def test_user_has_uuid_id(self, valid_user_email: str) -> None:
        """User.id should be a valid UUID, auto-generated."""
        from src.models.user import User

        user = User(
            email=valid_user_email,
            password_hash="hashed_password_here"
        )

        assert user.id is not None
        assert isinstance(user.id, UUID)

    def test_user_has_created_at_timestamp(self, valid_user_email: str) -> None:
        """User.created_at should be auto-populated with UTC timestamp."""
        from src.models.user import User

        before = datetime.now(timezone.utc)
        user = User(
            email=valid_user_email,
            password_hash="hashed_password_here"
        )
        after = datetime.now(timezone.utc)

        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
        assert before <= user.created_at <= after

    def test_user_has_updated_at_timestamp(self, valid_user_email: str) -> None:
        """User.updated_at should be auto-populated with UTC timestamp."""
        from src.models.user import User

        user = User(
            email=valid_user_email,
            password_hash="hashed_password_here"
        )

        assert user.updated_at is not None
        assert isinstance(user.updated_at, datetime)

    def test_user_stores_email(self, valid_user_email: str) -> None:
        """User should store email correctly."""
        from src.models.user import User

        user = User(
            email=valid_user_email,
            password_hash="hashed_password_here"
        )

        assert user.email == valid_user_email

    def test_user_stores_password_hash(self, valid_user_email: str) -> None:
        """User should store password_hash (not plain password)."""
        from src.models.user import User

        password_hash = "$argon2id$v=19$m=65536,t=3,p=4$..."
        user = User(
            email=valid_user_email,
            password_hash=password_hash
        )

        assert user.password_hash == password_hash


# =============================================================================
# T012: UserCreate Validation Tests
# =============================================================================

@pytest.mark.unit
class TestUserCreateValidation:
    """Test UserCreate schema validation."""

    def test_valid_user_create(
        self, valid_user_email: str, valid_password: str
    ) -> None:
        """UserCreate should accept valid email and password."""
        from src.models.user import UserCreate

        user_create = UserCreate(
            email=valid_user_email,
            password=valid_password
        )

        assert user_create.email == valid_user_email
        assert user_create.password == valid_password

    def test_invalid_email_format_rejected(
        self, invalid_emails: list[str], valid_password: str
    ) -> None:
        """UserCreate should reject invalid email formats."""
        from pydantic import ValidationError
        from src.models.user import UserCreate

        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(email=invalid_email, password=valid_password)

            # Should have email validation error
            errors = exc_info.value.errors()
            assert any(
                "email" in str(e.get("loc", []))
                for e in errors
            ), f"Expected email error for: {invalid_email}"

    def test_password_too_short_rejected(
        self, valid_user_email: str, invalid_passwords: list[str]
    ) -> None:
        """UserCreate should reject passwords shorter than 8 characters."""
        from pydantic import ValidationError
        from src.models.user import UserCreate

        for short_password in invalid_passwords:
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(email=valid_user_email, password=short_password)

            # Should have password validation error
            errors = exc_info.value.errors()
            assert any(
                "password" in str(e.get("loc", []))
                for e in errors
            ), f"Expected password error for length {len(short_password)}"

    def test_password_minimum_length_accepted(
        self, valid_user_email: str
    ) -> None:
        """UserCreate should accept password with exactly 8 characters."""
        from src.models.user import UserCreate

        min_password = "12345678"  # Exactly 8 chars
        user_create = UserCreate(
            email=valid_user_email,
            password=min_password
        )

        assert len(user_create.password) == 8


# =============================================================================
# T013: UserPublic Schema Tests
# =============================================================================

@pytest.mark.unit
class TestUserPublicSchema:
    """Test UserPublic schema excludes sensitive fields."""

    def test_user_public_excludes_password_hash(
        self, valid_user_email: str
    ) -> None:
        """UserPublic should NOT include password_hash field."""
        from src.models.user import User, UserPublic
        from uuid import uuid4
        from datetime import datetime, timezone

        # Create a User with password_hash
        user = User(
            id=uuid4(),
            email=valid_user_email,
            password_hash="secret_hash_value",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Convert to UserPublic
        user_public = UserPublic.model_validate(user)

        # password_hash should not be in the model
        assert not hasattr(user_public, "password_hash")
        # Verify it's not in the dict output
        user_dict = user_public.model_dump()
        assert "password_hash" not in user_dict

    def test_user_public_includes_safe_fields(
        self, valid_user_email: str
    ) -> None:
        """UserPublic should include id, email, timestamps."""
        from src.models.user import User, UserPublic
        from uuid import uuid4
        from datetime import datetime, timezone

        user_id = uuid4()
        created = datetime.now(timezone.utc)
        updated = datetime.now(timezone.utc)

        user = User(
            id=user_id,
            email=valid_user_email,
            password_hash="secret_hash_value",
            created_at=created,
            updated_at=updated,
        )

        user_public = UserPublic.model_validate(user)

        assert user_public.id == user_id
        assert user_public.email == valid_user_email
        assert user_public.created_at == created
        assert user_public.updated_at == updated
