class TodoError(Exception):
    """Base class for application-specific errors."""


class ParseError(TodoError):
    """Raised when input parsing (dates, locations) fails."""


class ServiceError(TodoError):
    """Raised when an external service (geocoding/weather) returns error or is unavailable."""


class StorageError(TodoError):
    """Raised for storage-related problems (IO, locking).

    Attributes:
        path: optional path that caused the error
    """

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message)
        self.path = path
