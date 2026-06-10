"""Tests for SystemPrompt."""

import pytest

from learning_assistant.prompts.exceptions import ValidationError
from learning_assistant.prompts.system_prompt import SystemPrompt


class TestSystemPrompt:
    def test_name_and_version(self) -> None:
        p = SystemPrompt()
        assert p.name == "system"
        assert p.version == "v1"

    def test_required_variables(self) -> None:
        p = SystemPrompt()
        assert "custom_instructions" in p.required_variables

    def test_render_with_instructions(self) -> None:
        p = SystemPrompt()
        result = p.render(custom_instructions="Be helpful.")
        assert "Be helpful." in result
        assert "learning assistant" in result.lower()

    def test_render_missing_variable_raises(self) -> None:
        p = SystemPrompt()
        with pytest.raises(ValidationError, match="Missing"):
            p.render()

    def test_custom_template(self) -> None:
        template = "Custom system: {custom_instructions}"
        p = SystemPrompt(template=template)
        result = p.render(custom_instructions="Hello")
        assert result == "Custom system: Hello"
