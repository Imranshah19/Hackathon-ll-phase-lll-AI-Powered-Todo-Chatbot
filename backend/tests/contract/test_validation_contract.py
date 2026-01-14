"""
Contract tests for ValidationError schema.

Tests:
- T042: Validate ValidationError matches OpenAPI specification
"""

import pytest
from pydantic import ValidationError


@pytest.mark.contract
class TestValidationErrorContract:
    """Contract tests ensuring validation errors match API specification."""

    def test_validation_error_structure_matches_openapi(self) -> None:
        """ValidationError structure should match OpenAPI ValidationError schema.

        OpenAPI spec defines:
        - detail: array of ValidationErrorItem
          - loc: array of strings/integers (field path)
          - msg: string (human-readable message)
          - type: string (error type identifier)
        """
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid", password="short")

        # Get errors in JSON-serializable format
        errors = exc_info.value.errors()

        # Verify structure matches OpenAPI
        assert isinstance(errors, list), "Errors should be a list"
        assert len(errors) > 0, "Should have at least one error"

        for error in errors:
            # Each error should have loc, msg, type
            assert "loc" in error, "Error should have 'loc'"
            assert "msg" in error, "Error should have 'msg'"
            assert "type" in error, "Error should have 'type'"

            # loc should be a sequence (tuple or list)
            assert isinstance(error["loc"], (list, tuple)), "loc should be array"

            # msg should be non-empty string
            assert isinstance(error["msg"], str), "msg should be string"
            assert len(error["msg"]) > 0, "msg should not be empty"

            # type should be non-empty string
            assert isinstance(error["type"], str), "type should be string"
            assert len(error["type"]) > 0, "type should not be empty"

    def test_validation_error_json_serializable(self) -> None:
        """ValidationError should be JSON serializable for API response."""
        import json
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid", password="short")

        # Should be JSON serializable
        errors = exc_info.value.errors()

        # Convert to JSON and back
        json_str = json.dumps({"detail": errors})
        parsed = json.loads(json_str)

        assert "detail" in parsed
        assert isinstance(parsed["detail"], list)

    def test_validation_error_loc_identifies_field(self) -> None:
        """ValidationError.loc should correctly identify the problematic field."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid", password="validpassword123")

        errors = exc_info.value.errors()
        email_error = next(
            (e for e in errors if "email" in str(e["loc"])),
            None
        )

        assert email_error is not None, "Should have email error with loc"
        assert "email" in str(email_error["loc"]), "loc should contain 'email'"

    def test_validation_error_type_is_descriptive(self) -> None:
        """ValidationError.type should be a descriptive error type identifier."""
        from src.models.task import TaskCreate

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")  # Empty title

        errors = exc_info.value.errors()
        title_error = next(
            (e for e in errors if "title" in str(e["loc"])),
            None
        )

        assert title_error is not None, "Should have title error"
        # Type should be something like "string_too_short" or similar
        assert isinstance(title_error["type"], str)
        assert "_" in title_error["type"] or title_error["type"].islower(), \
            "Type should be snake_case identifier"

    def test_email_validation_error_format(self) -> None:
        """Email validation error should have correct format."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="not-an-email", password="password123")

        errors = exc_info.value.errors()
        email_error = next(
            (e for e in errors if "email" in str(e["loc"])),
            None
        )

        assert email_error is not None
        assert email_error["type"] in [
            "value_error",
            "value_error.email",
            "string_type",
            "value_error.invalid_email",
        ] or "email" in email_error["type"].lower()

    def test_string_length_validation_error_format(self) -> None:
        """String length validation error should have correct format."""
        from src.models.task import TaskCreate

        # Test too short
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")

        errors = exc_info.value.errors()
        title_error = next(
            (e for e in errors if "title" in str(e["loc"])),
            None
        )

        assert title_error is not None
        # Should indicate string is too short
        assert "short" in title_error["type"] or "min" in title_error["type"].lower() \
            or "length" in title_error["type"].lower()

    def test_max_length_validation_error_format(self) -> None:
        """Max length validation error should have correct format."""
        from src.models.task import TaskCreate

        # Test too long
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="x" * 256)

        errors = exc_info.value.errors()
        title_error = next(
            (e for e in errors if "title" in str(e["loc"])),
            None
        )

        assert title_error is not None
        # Should indicate string is too long
        assert "long" in title_error["type"] or "max" in title_error["type"].lower() \
            or "length" in title_error["type"].lower()

    def test_missing_field_validation_error_format(self) -> None:
        """Missing required field should have correct error format."""
        from src.models.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate()  # Missing both email and password

        errors = exc_info.value.errors()

        # Should have errors for missing fields
        assert len(errors) >= 2, "Should have multiple missing field errors"

        for error in errors:
            # Missing field errors typically have type "missing"
            assert "missing" in error["type"].lower() or "required" in error["msg"].lower()

    def test_nested_field_loc_format(self) -> None:
        """Nested field errors should have properly formatted loc."""
        from src.models.user import UserCreate

        # When validated as part of a request body, loc might be ["body", "email"]
        # For direct model validation, it's just ("email",)
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid", password="short")

        errors = exc_info.value.errors()

        for error in errors:
            loc = error["loc"]
            # loc should be a tuple/list with at least the field name
            assert len(loc) >= 1, "loc should have at least one element"
            # Last element should be the field name
            assert isinstance(loc[-1], str), "Field name should be string"
