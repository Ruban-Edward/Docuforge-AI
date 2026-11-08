"""Custom Application Exceptions with HTTP status codes and standardized error structures."""

from typing import Any, Optional
from fastapi import status
from app.core.constants import ErrorCode


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND, details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_404_NOT_FOUND, details=details)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required", code: ErrorCode = ErrorCode.UNAUTHORIZED, details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Access forbidden", code: ErrorCode = ErrorCode.FORBIDDEN, details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_403_FORBIDDEN, details=details)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed", code: ErrorCode = ErrorCode.VALIDATION_ERROR, details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource conflict", code: ErrorCode = ErrorCode.RESOURCE_ALREADY_EXISTS, details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_409_CONFLICT, details=details)

