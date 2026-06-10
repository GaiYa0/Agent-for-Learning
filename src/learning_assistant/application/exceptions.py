"""Application-layer exception hierarchy."""


class ApplicationError(Exception):
    """Base for all application errors."""


class ValidationError(ApplicationError):
    """Raised when request validation fails."""


class NotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""


class WorkflowError(ApplicationError):
    """Raised when a workflow fails."""


class SessionError(ApplicationError):
    """Raised when session operations fail."""
