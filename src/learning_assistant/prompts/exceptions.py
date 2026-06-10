"""Prompt-layer exception hierarchy."""


class PromptError(Exception):
    """Base for all prompt errors."""


class TemplateNotFoundError(PromptError):
    """Raised when a template is not registered."""


class RenderError(PromptError):
    """Raised when template rendering fails."""


class ValidationError(PromptError):
    """Raised when prompt validation fails."""
