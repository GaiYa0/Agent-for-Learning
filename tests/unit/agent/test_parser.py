"""Tests for ReActParser."""

import pytest

from learning_assistant.agent.exceptions import ParseError
from learning_assistant.agent.parser import ReActParser


@pytest.fixture()
def parser() -> ReActParser:
    return ReActParser()


class TestReActParser:
    def test_parse_final_answer(self, parser: ReActParser) -> None:
        text = "Thought: I have enough info.\nFinal Answer: Python is great."
        action = parser.parse(text)
        assert action.is_final is True
        assert action.final_answer == "Python is great."
        assert action.thought == "I have enough info."

    def test_parse_action(self, parser: ReActParser) -> None:
        text = (
            "Thought: I need to search.\n"
            "Action: web_search\n"
            "Action Input: Python tutorials"
        )
        action = parser.parse(text)
        assert action.is_final is False
        assert action.action == "web_search"
        assert action.action_input == "Python tutorials"
        assert action.thought == "I need to search."

    def test_parse_empty_raises(self, parser: ReActParser) -> None:
        with pytest.raises(ParseError, match="Empty"):
            parser.parse("")

    def test_parse_no_action_raises(self, parser: ReActParser) -> None:
        with pytest.raises(ParseError, match="No Action"):
            parser.parse("Just some random text")

    def test_parse_final_without_thought(self, parser: ReActParser) -> None:
        text = "Final Answer: The answer is 42."
        action = parser.parse(text)
        assert action.is_final is True
        assert action.final_answer == "The answer is 42."

    def test_parse_action_without_input(self, parser: ReActParser) -> None:
        text = "Thought: Need tool.\nAction: calculator"
        action = parser.parse(text)
        assert action.action == "calculator"
        assert action.action_input == ""

    def test_parse_action_finish(self, parser: ReActParser) -> None:
        text = (
            "Thought: Done.\n"
            "Action: finish\n"
            "Action Input: The answer is 42."
        )
        action = parser.parse(text)
        assert action.is_final is True
        assert action.final_answer == "The answer is 42."

    def test_parse_multiline_thought(self, parser: ReActParser) -> None:
        text = (
            "Thought: Line one.\nLine two.\n"
            "Action: search\n"
            "Action Input: query"
        )
        action = parser.parse(text)
        assert "Line one" in action.thought
