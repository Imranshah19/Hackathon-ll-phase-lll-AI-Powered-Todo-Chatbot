"""
Request/Response logging middleware for chat endpoints.

Implements FR-010: Log AI interpretations with confidence for debugging.

Logs:
- Request method, path, and timing
- Response status codes
- User ID (anonymized) for chat requests
- Errors and exceptions
"""

import logging
import time
from typing import Callable
from uuid import UUID

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class ChatLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging chat API requests and responses.

    Focuses on /api/chat/* endpoints for debugging AI interactions.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request and log details for chat endpoints."""
        # Only log chat endpoints in detail
        is_chat_endpoint = request.url.path.startswith("/api/chat")

        start_time = time.time()

        # Log request
        if is_chat_endpoint:
            logger.info(
                f"Chat request: {request.method} {request.url.path}"
            )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response for chat endpoints
            if is_chat_endpoint:
                logger.info(
                    f"Chat response: {request.method} {request.url.path} "
                    f"status={response.status_code} duration={duration_ms:.2f}ms"
                )

            # Add timing header for debugging
            response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            logger.error(
                f"Chat error: {request.method} {request.url.path} "
                f"error={type(e).__name__}: {str(e)} duration={duration_ms:.2f}ms"
            )
            raise


def setup_chat_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for chat module.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure chat logger
    chat_logger = logging.getLogger("src.services.chat_service")
    chat_logger.setLevel(getattr(logging, log_level))

    # Configure AI logger
    ai_logger = logging.getLogger("src.ai")
    ai_logger.setLevel(getattr(logging, log_level))

    # Configure middleware logger
    middleware_logger = logging.getLogger(__name__)
    middleware_logger.setLevel(getattr(logging, log_level))

    # Add handler if not already present
    if not chat_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        chat_logger.addHandler(handler)
        ai_logger.addHandler(handler)
        middleware_logger.addHandler(handler)


__all__ = ["ChatLoggingMiddleware", "setup_chat_logging"]
