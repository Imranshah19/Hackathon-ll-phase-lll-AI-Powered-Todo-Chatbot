"""
Failure mode models and enums.

T007: FailureCode enum
T008: Severity enum
T009: STANDARD_FAILURE_MODES mapping
T012: FailureResponse model
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class FailureCode(str, Enum):
    """
    Standard failure codes for skill errors.

    See: phase-2/skills.spec.md Section 9.1
    """

    # Input errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    """Input failed schema validation"""

    INVALID_PATH = "INVALID_PATH"
    """Path does not match any route"""

    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    """HTTP method not supported"""

    MALFORMED_REQUEST = "MALFORMED_REQUEST"
    """Request structure invalid"""

    INVALID_QUERY = "INVALID_QUERY"
    """Query parameters invalid"""

    # Data errors
    NOT_FOUND = "NOT_FOUND"
    """Resource doesn't exist"""

    DUPLICATE_EMAIL = "DUPLICATE_EMAIL"
    """Email already registered"""

    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    """Specific resource doesn't exist"""

    # Security errors
    UNAUTHORIZED = "UNAUTHORIZED"
    """Permission denied"""

    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    """Token signature doesn't match"""

    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    """Token past expiration"""

    MALFORMED_TOKEN = "MALFORMED_TOKEN"
    """Token structure invalid"""

    WEAK_PASSWORD = "WEAK_PASSWORD"
    """Password doesn't meet requirements"""

    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    """Session doesn't exist"""

    SESSION_EXPIRED = "SESSION_EXPIRED"
    """Cannot refresh expired session"""

    # Rate limiting
    RATE_EXCEEDED = "RATE_EXCEEDED"
    """Too many requests"""

    # Execution errors
    TIMEOUT = "TIMEOUT"
    """Operation took too long"""

    PERSISTENCE_ERROR = "PERSISTENCE_ERROR"
    """Database operation failed"""

    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    """External API failed"""

    INTERNAL_ERROR = "INTERNAL_ERROR"
    """Unexpected system failure"""

    # Workflow errors
    STEP_FAILED = "STEP_FAILED"
    """Workflow step returned error"""

    ROLLBACK_FAILED = "ROLLBACK_FAILED"
    """Unable to undo partial changes"""

    WORKFLOW_TIMEOUT = "WORKFLOW_TIMEOUT"
    """Workflow exceeded time limit"""

    MERGE_CONFLICT = "MERGE_CONFLICT"
    """Incompatible response structures"""

    ALL_FAILED = "ALL_FAILED"
    """Every agent returned error"""

    # Crypto errors
    HASH_FAILURE = "HASH_FAILURE"
    """Cryptographic operation failed"""

    SIGNING_FAILURE = "SIGNING_FAILURE"
    """Unable to sign token"""

    INVALID_CLAIMS = "INVALID_CLAIMS"
    """Claims contain invalid data"""

    # Store errors
    STORE_UNAVAILABLE = "STORE_UNAVAILABLE"
    """Rate limit store unreachable"""

    LOG_FAILURE = "LOG_FAILURE"
    """Unable to persist error log"""

    # AI errors
    AI_UNAVAILABLE = "AI_UNAVAILABLE"
    """AI service unreachable"""

    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    """Not enough data to process"""

    # Planning errors
    AMBIGUOUS_GOAL = "AMBIGUOUS_GOAL"
    """Cannot interpret user intent"""

    GOAL_TOO_COMPLEX = "GOAL_TOO_COMPLEX"
    """Exceeds decomposition limits"""

    CIRCULAR_DEPENDENCY = "CIRCULAR_DEPENDENCY"
    """Tasks have circular references"""

    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    """Referenced task not in list"""

    STATE_UNKNOWN = "STATE_UNKNOWN"
    """Cannot determine current state"""

    # Execution errors
    EXECUTION_ERROR = "EXECUTION_ERROR"
    """Task logic failed"""

    AGENT_UNAVAILABLE = "AGENT_UNAVAILABLE"
    """Required agent not responding"""

    REPORTING_FAILED = "REPORTING_FAILED"
    """Unable to send update"""

    MAX_RETRIES_EXCEEDED = "MAX_RETRIES_EXCEEDED"
    """All attempts exhausted"""

    # Cascade errors
    CASCADE_FAILED = "CASCADE_FAILED"
    """Unable to delete dependent resources"""


class Severity(str, Enum):
    """
    Severity levels for failures.

    See: phase-2/skills.spec.md Section 9.1
    """

    RECOVERABLE = "recoverable"
    """Error that can be retried or handled gracefully"""

    FATAL = "fatal"
    """Error that cannot be recovered from"""


class FailureModeDefinition(BaseModel):
    """Definition of a failure mode with its metadata."""

    code: FailureCode
    message: str
    severity: Severity
    retryable: bool = False
    http_status: int = 500


# T009: Standard failure modes mapping
STANDARD_FAILURE_MODES: dict[FailureCode, FailureModeDefinition] = {
    # Input errors (400)
    FailureCode.VALIDATION_ERROR: FailureModeDefinition(
        code=FailureCode.VALIDATION_ERROR,
        message="Input failed schema validation",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=400,
    ),
    FailureCode.INVALID_PATH: FailureModeDefinition(
        code=FailureCode.INVALID_PATH,
        message="Path does not match any route",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=404,
    ),
    FailureCode.METHOD_NOT_ALLOWED: FailureModeDefinition(
        code=FailureCode.METHOD_NOT_ALLOWED,
        message="HTTP method not supported",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=405,
    ),
    FailureCode.MALFORMED_REQUEST: FailureModeDefinition(
        code=FailureCode.MALFORMED_REQUEST,
        message="Request structure invalid",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=400,
    ),
    FailureCode.INVALID_QUERY: FailureModeDefinition(
        code=FailureCode.INVALID_QUERY,
        message="Query parameters invalid",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=400,
    ),
    # Data errors (404, 409)
    FailureCode.NOT_FOUND: FailureModeDefinition(
        code=FailureCode.NOT_FOUND,
        message="Resource doesn't exist",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=404,
    ),
    FailureCode.RESOURCE_NOT_FOUND: FailureModeDefinition(
        code=FailureCode.RESOURCE_NOT_FOUND,
        message="Specific resource doesn't exist",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=404,
    ),
    FailureCode.DUPLICATE_EMAIL: FailureModeDefinition(
        code=FailureCode.DUPLICATE_EMAIL,
        message="Email already registered",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=409,
    ),
    # Security errors (401, 403)
    FailureCode.UNAUTHORIZED: FailureModeDefinition(
        code=FailureCode.UNAUTHORIZED,
        message="Permission denied",
        severity=Severity.FATAL,
        retryable=False,
        http_status=403,
    ),
    FailureCode.INVALID_SIGNATURE: FailureModeDefinition(
        code=FailureCode.INVALID_SIGNATURE,
        message="Token signature doesn't match",
        severity=Severity.FATAL,
        retryable=False,
        http_status=401,
    ),
    FailureCode.TOKEN_EXPIRED: FailureModeDefinition(
        code=FailureCode.TOKEN_EXPIRED,
        message="Token past expiration",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=401,
    ),
    FailureCode.MALFORMED_TOKEN: FailureModeDefinition(
        code=FailureCode.MALFORMED_TOKEN,
        message="Token structure invalid",
        severity=Severity.FATAL,
        retryable=False,
        http_status=401,
    ),
    FailureCode.WEAK_PASSWORD: FailureModeDefinition(
        code=FailureCode.WEAK_PASSWORD,
        message="Password doesn't meet requirements",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=400,
    ),
    FailureCode.SESSION_NOT_FOUND: FailureModeDefinition(
        code=FailureCode.SESSION_NOT_FOUND,
        message="Session doesn't exist",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=404,
    ),
    FailureCode.SESSION_EXPIRED: FailureModeDefinition(
        code=FailureCode.SESSION_EXPIRED,
        message="Cannot refresh expired session",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=401,
    ),
    # Rate limiting (429)
    FailureCode.RATE_EXCEEDED: FailureModeDefinition(
        code=FailureCode.RATE_EXCEEDED,
        message="Too many requests",
        severity=Severity.RECOVERABLE,
        retryable=True,
        http_status=429,
    ),
    # Execution errors (500, 503, 504)
    FailureCode.TIMEOUT: FailureModeDefinition(
        code=FailureCode.TIMEOUT,
        message="Operation took too long",
        severity=Severity.RECOVERABLE,
        retryable=True,
        http_status=504,
    ),
    FailureCode.PERSISTENCE_ERROR: FailureModeDefinition(
        code=FailureCode.PERSISTENCE_ERROR,
        message="Database operation failed",
        severity=Severity.RECOVERABLE,
        retryable=True,
        http_status=503,
    ),
    FailureCode.EXTERNAL_SERVICE_ERROR: FailureModeDefinition(
        code=FailureCode.EXTERNAL_SERVICE_ERROR,
        message="External API failed",
        severity=Severity.RECOVERABLE,
        retryable=True,
        http_status=503,
    ),
    FailureCode.INTERNAL_ERROR: FailureModeDefinition(
        code=FailureCode.INTERNAL_ERROR,
        message="Unexpected system failure",
        severity=Severity.FATAL,
        retryable=False,
        http_status=500,
    ),
    # Workflow errors
    FailureCode.STEP_FAILED: FailureModeDefinition(
        code=FailureCode.STEP_FAILED,
        message="Workflow step returned error",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=500,
    ),
    FailureCode.ROLLBACK_FAILED: FailureModeDefinition(
        code=FailureCode.ROLLBACK_FAILED,
        message="Unable to undo partial changes",
        severity=Severity.FATAL,
        retryable=False,
        http_status=500,
    ),
    FailureCode.WORKFLOW_TIMEOUT: FailureModeDefinition(
        code=FailureCode.WORKFLOW_TIMEOUT,
        message="Workflow exceeded time limit",
        severity=Severity.RECOVERABLE,
        retryable=True,
        http_status=504,
    ),
    FailureCode.MERGE_CONFLICT: FailureModeDefinition(
        code=FailureCode.MERGE_CONFLICT,
        message="Incompatible response structures",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=500,
    ),
    FailureCode.ALL_FAILED: FailureModeDefinition(
        code=FailureCode.ALL_FAILED,
        message="Every agent returned error",
        severity=Severity.FATAL,
        retryable=False,
        http_status=500,
    ),
    # Crypto errors
    FailureCode.HASH_FAILURE: FailureModeDefinition(
        code=FailureCode.HASH_FAILURE,
        message="Cryptographic operation failed",
        severity=Severity.FATAL,
        retryable=False,
        http_status=500,
    ),
    FailureCode.SIGNING_FAILURE: FailureModeDefinition(
        code=FailureCode.SIGNING_FAILURE,
        message="Unable to sign token",
        severity=Severity.FATAL,
        retryable=False,
        http_status=500,
    ),
    FailureCode.INVALID_CLAIMS: FailureModeDefinition(
        code=FailureCode.INVALID_CLAIMS,
        message="Claims contain invalid data",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=400,
    ),
    # Store errors
    FailureCode.STORE_UNAVAILABLE: FailureModeDefinition(
        code=FailureCode.STORE_UNAVAILABLE,
        message="Rate limit store unreachable",
        severity=Severity.RECOVERABLE,
        retryable=True,
        http_status=503,
    ),
    FailureCode.LOG_FAILURE: FailureModeDefinition(
        code=FailureCode.LOG_FAILURE,
        message="Unable to persist error log",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=500,
    ),
    # AI errors
    FailureCode.AI_UNAVAILABLE: FailureModeDefinition(
        code=FailureCode.AI_UNAVAILABLE,
        message="AI service unreachable",
        severity=Severity.RECOVERABLE,
        retryable=True,
        http_status=503,
    ),
    FailureCode.INSUFFICIENT_DATA: FailureModeDefinition(
        code=FailureCode.INSUFFICIENT_DATA,
        message="Not enough data to process",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=400,
    ),
    # Planning errors
    FailureCode.AMBIGUOUS_GOAL: FailureModeDefinition(
        code=FailureCode.AMBIGUOUS_GOAL,
        message="Cannot interpret user intent",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=400,
    ),
    FailureCode.GOAL_TOO_COMPLEX: FailureModeDefinition(
        code=FailureCode.GOAL_TOO_COMPLEX,
        message="Exceeds decomposition limits",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=400,
    ),
    FailureCode.CIRCULAR_DEPENDENCY: FailureModeDefinition(
        code=FailureCode.CIRCULAR_DEPENDENCY,
        message="Tasks have circular references",
        severity=Severity.FATAL,
        retryable=False,
        http_status=400,
    ),
    FailureCode.MISSING_DEPENDENCY: FailureModeDefinition(
        code=FailureCode.MISSING_DEPENDENCY,
        message="Referenced task not in list",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=400,
    ),
    FailureCode.STATE_UNKNOWN: FailureModeDefinition(
        code=FailureCode.STATE_UNKNOWN,
        message="Cannot determine current state",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=500,
    ),
    # Execution errors
    FailureCode.EXECUTION_ERROR: FailureModeDefinition(
        code=FailureCode.EXECUTION_ERROR,
        message="Task logic failed",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=500,
    ),
    FailureCode.AGENT_UNAVAILABLE: FailureModeDefinition(
        code=FailureCode.AGENT_UNAVAILABLE,
        message="Required agent not responding",
        severity=Severity.RECOVERABLE,
        retryable=True,
        http_status=503,
    ),
    FailureCode.REPORTING_FAILED: FailureModeDefinition(
        code=FailureCode.REPORTING_FAILED,
        message="Unable to send update",
        severity=Severity.RECOVERABLE,
        retryable=False,
        http_status=500,
    ),
    FailureCode.MAX_RETRIES_EXCEEDED: FailureModeDefinition(
        code=FailureCode.MAX_RETRIES_EXCEEDED,
        message="All attempts exhausted",
        severity=Severity.FATAL,
        retryable=False,
        http_status=500,
    ),
    # Cascade errors
    FailureCode.CASCADE_FAILED: FailureModeDefinition(
        code=FailureCode.CASCADE_FAILED,
        message="Unable to delete dependent resources",
        severity=Severity.FATAL,
        retryable=False,
        http_status=500,
    ),
}


class FailureDetails(BaseModel):
    """Context-specific details about a failure."""

    field: str | None = None
    """Which field failed (for validation errors)"""

    expected: str | None = None
    """What was expected"""

    actual: str | None = None
    """What was received"""

    additional: dict[str, Any] = Field(default_factory=dict)
    """Additional context-specific data"""


class FailureResponse(BaseModel):
    """
    Standardized failure response for skill errors.

    T012: FailureResponse model
    See: phase-2/skills.spec.md Section 9.2
    """

    code: FailureCode
    """Standard failure code"""

    message: str
    """Human-readable explanation (safe for client)"""

    details: FailureDetails | None = None
    """Context-specific data"""

    correlation_id: UUID
    """For troubleshooting"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    """When the failure occurred"""

    recoverable: bool
    """Can operation be retried?"""

    retry_after: int | None = None
    """Seconds to wait before retry (if applicable)"""

    @classmethod
    def from_code(
        cls,
        code: FailureCode,
        correlation_id: UUID,
        details: FailureDetails | None = None,
        message_override: str | None = None,
        retry_after: int | None = None,
    ) -> "FailureResponse":
        """
        Factory method to create a FailureResponse from a failure code.

        Uses STANDARD_FAILURE_MODES to populate defaults.
        """
        mode = STANDARD_FAILURE_MODES.get(code)
        if mode is None:
            # Fallback for unknown codes
            return cls(
                code=code,
                message=message_override or "Unknown error",
                details=details,
                correlation_id=correlation_id,
                recoverable=False,
                retry_after=retry_after,
            )

        return cls(
            code=code,
            message=message_override or mode.message,
            details=details,
            correlation_id=correlation_id,
            recoverable=mode.severity == Severity.RECOVERABLE,
            retry_after=retry_after if mode.retryable else None,
        )

    def to_http_status(self) -> int:
        """Get the HTTP status code for this failure."""
        mode = STANDARD_FAILURE_MODES.get(self.code)
        return mode.http_status if mode else 500
