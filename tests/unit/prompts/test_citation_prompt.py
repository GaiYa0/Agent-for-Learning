"""Tests for CitationPrompt."""

import pytest

from learning_assistant.prompts.citation_prompt import CitationPrompt
from learning_assistant.prompts.exceptions import ValidationError


class TestCitationPrompt:
    def test_name_and_version(self) -> None:
        p = CitationPrompt()
        assert p.name == "citation"
        assert p.version == "v1"

    def test_render(self) -> None:
        p = CitationPrompt()
        result = p.render(
            answer="Python is great.",
            sources="[1] python.org\n[2] docs.python.org",
        )
        assert "Python is great." in result
        assert "python.org" in result

    def test_missing_variable_raises(self) -> None:
        p = CitationPrompt()
        with pytest.raises(ValidationError, match="Missing"):
            p.render(answer="A")
