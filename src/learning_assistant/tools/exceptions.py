"""Tool-layer exception hierarchy."""


class ToolError(Exception):
    """Base for all tool errors."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""


class ToolExecutionError(ToolError):
    """Raised when a tool fails during execution."""


class ToolValidationError(ToolError):
    """Raised when tool input fails validation."""


class ToolRegistrationError(ToolError):
    """Raised when tool registration fails."""
