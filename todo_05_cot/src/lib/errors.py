class ApplicationError(Exception):
    """Base class for application-specific errors."""
    pass


class ValidationError(ApplicationError):
    """Raised when user input fails validation."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field


class NotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""
    pass


class ExternalAPIError(ApplicationError):
    """Raised when an external API call fails or returns invalid data."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ConfigError(ApplicationError):
    """Raised when configuration is missing or invalid."""
    pass
