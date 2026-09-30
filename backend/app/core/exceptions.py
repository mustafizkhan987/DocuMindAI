"""
DocuMind AI — Centralized Exception Handling
============================================

Custom application exceptions and FastAPI error handlers.
Ensures uniform JSON error responses and prevents sensitive data leaks.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class DocuMindException(Exception):
    """Base exception class for DocuMind AI application errors."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(DocuMindException):
    """Exception raised when a requested resource is not found."""

    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with id '{entity_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"entity_name": entity_name, "entity_id": entity_id},
        )


class ValidationException(DocuMindException):
    """Exception raised for domain / business rule validation failures."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class DatabaseConnectionException(DocuMindException):
    """Exception raised when database operations fail."""

    def __init__(self, message: str = "Database connection error"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


async def documind_exception_handler(request: Request, exc: DocuMindException) -> JSONResponse:
    """Handler for application-specific DocuMindExceptions."""
    logger.warning(f"Application error [{exc.status_code}]: {exc.message} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled internal exceptions."""
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "An unexpected internal server error occurred.",
            "path": request.url.path,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app instance."""
    app.add_exception_handler(DocuMindException, documind_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
