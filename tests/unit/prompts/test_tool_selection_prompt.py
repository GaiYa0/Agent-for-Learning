"""Tests for ToolSelectionPrompt."""

import pytest

from learning_assistant.prompts.exceptions import ValidationError
from learning_assistant.prompts.tool_selection_prompt import ToolSelectionPrompt


class TestToolSelectionPrompt:
    def test_name_and_version(self) -> None:
        p = ToolSelectionPrompt()
        assert p.name == "tool_selection"
        assert p.version == "v1"

    def test_render(self) -> None:
        p = ToolSelectionPrompt()
        result = p.render(
            question="Summarize this PDF",
            tools="- pdf_reader: read PDF\n- web_search: search web",
        )
        assert "Summarize this PDF" in result
        assert "pdf_reader" in result
        assert "JSON" in result

    def test_missing_variable_raises(self) -> None:
        p = ToolSelectionPrompt()
        with pytest.raises(ValidationError, match="Missing"):
            p.render(question="Q")
