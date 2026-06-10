"""Tests for PromptRenderer."""

from pathlib import Path

import pytest

from learning_assistant.prompts.exceptions import RenderError
from learning_assistant.prompts.prompt_renderer import PromptRenderer


@pytest.fixture()
def renderer() -> PromptRenderer:
    template_dir = Path(__file__).parent.parent.parent.parent / "src" / "learning_assistant" / "prompts" / "templates"
    return PromptRenderer(template_dir)


class TestPromptRenderer:
    def test_render_system_template(self, renderer: PromptRenderer) -> None:
        result = renderer.render("system_v1.j2", custom_instructions="Be concise.")
        assert "Be concise." in result
        assert "learning assistant" in result.lower()

    def test_render_react_template(self, renderer: PromptRenderer) -> None:
        result = renderer.render(
            "react_v1.j2",
            question="What is AI?",
            tools="- search: search web",
            observations="None.",
        )
        assert "What is AI?" in result
        assert "Thought:" in result

    def test_render_tool_selection_template(
        self, renderer: PromptRenderer
    ) -> None:
        result = renderer.render(
            "tool_selection_v1.j2",
            question="Summarize PDF",
            tools="- pdf_reader: read PDF",
        )
        assert "Summarize PDF" in result
        assert "JSON" in result

    def test_render_missing_variable_raises(
        self, renderer: PromptRenderer
    ) -> None:
        with pytest.raises(RenderError):
            renderer.render("system_v1.j2")

    def test_render_nonexistent_template_raises(
        self, renderer: PromptRenderer
    ) -> None:
        with pytest.raises(RenderError):
            renderer.render("nonexistent.j2")

    def test_render_string(self, renderer: PromptRenderer) -> None:
        result = renderer.render_string("Hello {{ name }}", name="World")
        assert result == "Hello World"

    def test_render_string_missing_var_raises(
        self, renderer: PromptRenderer
    ) -> None:
        with pytest.raises(RenderError):
            renderer.render_string("Hello {{ name }}")
