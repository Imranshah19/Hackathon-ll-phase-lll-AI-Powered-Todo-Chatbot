"""
Pytest configuration and shared fixtures for the skills library tests.

Test Categories:
- unit: Fast, isolated tests for individual components
- integration: Tests that may use database or external services
- contract: Schema validation tests for skill inputs/outputs
"""

import pytest
from typing import Any, Generator
from uuid import uuid4


# =============================================================================
# Markers
# =============================================================================

def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "contract: Contract tests (schema validation)")
    config.addinivalue_line("markers", "slow: Slow tests (AI operations, etc.)")


# =============================================================================
# Common Fixtures
# =============================================================================

@pytest.fixture
def correlation_id() -> str:
    """Generate a unique correlation ID for test tracing."""
    return str(uuid4())


@pytest.fixture
def sample_user_id() -> str:
    """Generate a sample user UUID."""
    return str(uuid4())


@pytest.fixture
def sample_task_id() -> str:
    """Generate a sample task UUID."""
    return str(uuid4())


@pytest.fixture
def sample_task_data() -> dict[str, Any]:
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "A test task description",
        "is_completed": False,
        "metadata": {},
    }


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePassword123!",
    }


# =============================================================================
# Skill Testing Fixtures
# =============================================================================

@pytest.fixture
def skill_context(correlation_id: str, sample_user_id: str) -> dict[str, Any]:
    """Base context for skill execution."""
    return {
        "correlation_id": correlation_id,
        "user_id": sample_user_id,
        "timestamp": "2026-01-12T00:00:00Z",
    }


# =============================================================================
# Mock Fixtures (to be expanded in Phase 2)
# =============================================================================

@pytest.fixture
def mock_database() -> Generator[None, None, None]:
    """Mock database connection for unit tests."""
    # TODO: Implement in Phase 2 when database is configured
    yield


@pytest.fixture
def mock_ai_service() -> Generator[None, None, None]:
    """Mock AI service for unit tests."""
    # TODO: Implement in Phase 8 when AI skills are implemented
    yield
