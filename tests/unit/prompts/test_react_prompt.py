"""Tests for ReActPrompt."""

import pytest

from learning_assistant.prompts.exceptions import ValidationError
from learning_assistant.prompts.react_prompt import ReActPrompt


class TestReActPrompt:
    def test_name_and_version(self) -> None:
        p = ReActPrompt()
        assert p.name == "react"
        assert p.version == "v1"

    def test_required_variables(self) -> None:
        p = ReActPrompt()
        assert p.required_variables == {"question", "tools", "observations", "context"}

    def test_render_basic(self) -> None:
        p = ReActPrompt()
        result = p.render(
            question="What is Python?",
            tools="- pdf_reader: read PDF",
            observations="None yet.",
            context="",
        )
        assert "What is Python?" in result
        assert "pdf_reader" in result
        assert "Thought:" in result
        assert "Action:" in result

    def test_render_with_context(self) -> None:
        p = ReActPrompt()
        result = p.render(
            question="Q",
            tools="- t: desc",
            observations="None.",
            context="Some context.\n",
        )
        assert "Some context." in result

    def test_render_without_context_uses_default(self) -> None:
        p = ReActPrompt()
        result = p.render(question="Q", tools="- t: d", observations="None.", context="")
        assert "Question: Q" in result

    def test_missing_variable_raises(self) -> None:
        p = ReActPrompt()
        with pytest.raises(ValidationError, match="Missing"):
            p.render(question="Q")
