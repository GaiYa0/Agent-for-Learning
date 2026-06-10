"""Tests for prompt exceptions."""

from learning_assistant.prompts.exceptions import (
    PromptError,
    RenderError,
    TemplateNotFoundError,
    ValidationError,
)


class TestPromptExceptions:
    def test_hierarchy(self) -> None:
        assert issubclass(TemplateNotFoundError, PromptError)
        assert issubclass(RenderError, PromptError)
        assert issubclass(ValidationError, PromptError)

    def test_messages(self) -> None:
        assert str(TemplateNotFoundError("x")).endswith("x")
        assert str(RenderError("y")).endswith("y")
        assert str(ValidationError("z")).endswith("z")
