# app/exceptions.py
from fastapi import status


class ServiceError(Exception):
    """Base class for service-related exceptions."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UserAlreadyExistsError(ServiceError):
    """Exception raised when trying to register a user with an
    email that already exists."""
    def __init__(self, email: str):
        message = f"Email '{email}' is already registered."
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class WeakPasswordError(ServiceError):
    """Exception raised when a provided password does not meet strength
    requirements."""
    def __init__(self):
        message = "Password does not meet strength requirements."
        super().__init__(message)
