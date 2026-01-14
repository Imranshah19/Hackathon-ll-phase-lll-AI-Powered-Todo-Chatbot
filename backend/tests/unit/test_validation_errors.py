"""
Unit tests for validation error messages.

Tests:
- T038: Email validation errors
- T039: Password validation errors
- T040: Title validation errors
- T041: Description validation errors

Goal: Ensure consistent, user-friendly error messages across all schemas.
"""

import pytest
from pydantic import ValidationError


# =============================================================================
# T038: Email Validation Error Tests
# =============================================================================

@pytest.mark.unit
class TestEmailValidationErrors:
    """Test email validation produces correct error messages."""

    def test_invalid_email_format_error_message(self) -> None:
        """Invalid email should return 'Invalid email format' message."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="not-an-email", password="password123")

        errors = exc_info.value.errors()
        email_errors = [e for e in errors if "email" in str(e.get("loc", []))]

        assert len(email_errors) > 0, "Should have email validation error"
        # Check that error message is user-friendly
        error_msg = email_errors[0].get("msg", "").lower()
        assert "email" in error_msg or "invalid" in error_msg, \
            f"Error message should mention email issue: {error_msg}"

    def test_missing_email_error(self) -> None:
        """Missing email should produce a validation error."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(password="password123")  # Missing email

        errors = exc_info.value.errors()
        email_errors = [e for e in errors if "email" in str(e.get("loc", []))]
        assert len(email_errors) > 0, "Should have email required error"

    def test_empty_email_error(self) -> None:
        """Empty email should produce a validation error."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="", password="password123")

        errors = exc_info.value.errors()
        email_errors = [e for e in errors if "email" in str(e.get("loc", []))]
        assert len(email_errors) > 0, "Should have email validation error for empty string"


# =============================================================================
# T039: Password Validation Error Tests
# =============================================================================

@pytest.mark.unit
class TestPasswordValidationErrors:
    """Test password validation produces correct error messages."""

    def test_password_too_short_error_message(self) -> None:
        """Password < 8 chars should return appropriate error message."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="short")

        errors = exc_info.value.errors()
        password_errors = [e for e in errors if "password" in str(e.get("loc", []))]

        assert len(password_errors) > 0, "Should have password validation error"
        # Check error mentions length requirement
        error_msg = password_errors[0].get("msg", "").lower()
        assert "8" in error_msg or "character" in error_msg or "short" in error_msg or "least" in error_msg, \
            f"Error message should mention minimum length: {error_msg}"

    def test_password_exactly_7_chars_rejected(self) -> None:
        """Password with exactly 7 characters should be rejected."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="1234567")

        errors = exc_info.value.errors()
        password_errors = [e for e in errors if "password" in str(e.get("loc", []))]
        assert len(password_errors) > 0, "Should reject 7-char password"

    def test_missing_password_error(self) -> None:
        """Missing password should produce a validation error."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com")  # Missing password

        errors = exc_info.value.errors()
        password_errors = [e for e in errors if "password" in str(e.get("loc", []))]
        assert len(password_errors) > 0, "Should have password required error"

    def test_empty_password_error(self) -> None:
        """Empty password should produce a validation error."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="")

        errors = exc_info.value.errors()
        password_errors = [e for e in errors if "password" in str(e.get("loc", []))]
        assert len(password_errors) > 0, "Should have password validation error for empty string"


# =============================================================================
# T040: Title Validation Error Tests
# =============================================================================

@pytest.mark.unit
class TestTitleValidationErrors:
    """Test title validation produces correct error messages."""

    def test_empty_title_error_message(self) -> None:
        """Empty title should return appropriate error message."""
        from src.models.task import TaskCreate

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")

        errors = exc_info.value.errors()
        title_errors = [e for e in errors if "title" in str(e.get("loc", []))]

        assert len(title_errors) > 0, "Should have title validation error"
        # Check error indicates title is required/too short
        error_msg = title_errors[0].get("msg", "").lower()
        assert "1" in error_msg or "character" in error_msg or "short" in error_msg or "required" in error_msg, \
            f"Error message should indicate title is required: {error_msg}"

    def test_title_too_long_error_message(self) -> None:
        """Title > 255 chars should return appropriate error message."""
        from src.models.task import TaskCreate

        long_title = "x" * 256
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title)

        errors = exc_info.value.errors()
        title_errors = [e for e in errors if "title" in str(e.get("loc", []))]

        assert len(title_errors) > 0, "Should have title validation error"
        # Check error mentions length limit
        error_msg = title_errors[0].get("msg", "").lower()
        assert "255" in error_msg or "character" in error_msg or "long" in error_msg or "exceed" in error_msg, \
            f"Error message should mention max length: {error_msg}"

    def test_missing_title_error(self) -> None:
        """Missing title should produce a validation error."""
        from src.models.task import TaskCreate

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate()  # Missing title

        errors = exc_info.value.errors()
        title_errors = [e for e in errors if "title" in str(e.get("loc", []))]
        assert len(title_errors) > 0, "Should have title required error"

    def test_title_exactly_255_chars_accepted(self) -> None:
        """Title with exactly 255 characters should be accepted."""
        from src.models.task import TaskCreate

        max_title = "x" * 255
        task = TaskCreate(title=max_title)
        assert len(task.title) == 255


# =============================================================================
# T041: Description Validation Error Tests
# =============================================================================

@pytest.mark.unit
class TestDescriptionValidationErrors:
    """Test description validation produces correct error messages."""

    def test_description_too_long_error_message(self) -> None:
        """Description > 4000 chars should return appropriate error message."""
        from src.models.task import TaskCreate

        long_description = "x" * 4001
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Valid Title", description=long_description)

        errors = exc_info.value.errors()
        desc_errors = [e for e in errors if "description" in str(e.get("loc", []))]

        assert len(desc_errors) > 0, "Should have description validation error"
        # Check error mentions length limit
        error_msg = desc_errors[0].get("msg", "").lower()
        assert "4000" in error_msg or "character" in error_msg or "long" in error_msg or "exceed" in error_msg, \
            f"Error message should mention max length: {error_msg}"

    def test_description_exactly_4000_chars_accepted(self) -> None:
        """Description with exactly 4000 characters should be accepted."""
        from src.models.task import TaskCreate

        max_description = "x" * 4000
        task = TaskCreate(title="Valid Title", description=max_description)
        assert len(task.description) == 4000

    def test_description_none_accepted(self) -> None:
        """None description should be accepted (optional field)."""
        from src.models.task import TaskCreate

        task = TaskCreate(title="Valid Title", description=None)
        assert task.description is None

    def test_description_empty_string_accepted(self) -> None:
        """Empty string description should be accepted."""
        from src.models.task import TaskCreate

        task = TaskCreate(title="Valid Title", description="")
        assert task.description == ""


# =============================================================================
# Additional: Validation Error Structure Tests
# =============================================================================

@pytest.mark.unit
class TestValidationErrorStructure:
    """Test that validation errors have consistent structure."""

    def test_validation_error_has_loc(self) -> None:
        """Validation errors should include field location."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid", password="short")

        errors = exc_info.value.errors()
        for error in errors:
            assert "loc" in error, "Each error should have 'loc' field"
            assert isinstance(error["loc"], tuple), "loc should be a tuple"

    def test_validation_error_has_msg(self) -> None:
        """Validation errors should include human-readable message."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid", password="short")

        errors = exc_info.value.errors()
        for error in errors:
            assert "msg" in error, "Each error should have 'msg' field"
            assert isinstance(error["msg"], str), "msg should be a string"
            assert len(error["msg"]) > 0, "msg should not be empty"

    def test_validation_error_has_type(self) -> None:
        """Validation errors should include error type identifier."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid", password="short")

        errors = exc_info.value.errors()
        for error in errors:
            assert "type" in error, "Each error should have 'type' field"
            assert isinstance(error["type"], str), "type should be a string"

    def test_multiple_field_errors_reported(self) -> None:
        """Multiple validation errors should all be reported."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid", password="short")

        errors = exc_info.value.errors()
        # Should have errors for both email and password
        error_fields = [str(e.get("loc", [])) for e in errors]
        assert any("email" in f for f in error_fields), "Should have email error"
        assert any("password" in f for f in error_fields), "Should have password error"
