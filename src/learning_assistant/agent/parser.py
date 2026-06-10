"""ReAct output parser — extracts Thought/Action/Action Input/Final Answer."""

import re

from learning_assistant.agent.exceptions import ParseError
from learning_assistant.agent.state import AgentAction


class ReActParser:
    """Parses LLM output in ReAct format into AgentAction."""

    _THOUGHT_RE = re.compile(r"Thought:\s*(.+?)(?=\nAction:|\nFinal Answer:|\Z)", re.DOTALL)
    _ACTION_RE = re.compile(r"Action:\s*(.+?)(?=\n|$)", re.DOTALL)
    _INPUT_RE = re.compile(r"Action Input:\s*(.+?)(?=\nThought:|\nAction:|\nFinal Answer:|\Z)", re.DOTALL)
    _FINAL_RE = re.compile(r"Final Answer:\s*(.+)", re.DOTALL)

    def parse(self, text: str) -> AgentAction:
        text = text.strip()
        if not text:
            raise ParseError("Empty LLM output")

        final_match = self._FINAL_RE.search(text)
        if final_match:
            return AgentAction(
                thought=self._extract_thought(text),
                action="finish",
                action_input="",
                is_final=True,
                final_answer=final_match.group(1).strip(),
            )

        action_match = self._ACTION_RE.search(text)
        if not action_match:
            raise ParseError(f"No Action or Final Answer found in: {text[:200]}")

        action_name = action_match.group(1).strip()
        input_match = self._INPUT_RE.search(text)
        action_input = input_match.group(1).strip() if input_match else ""

        if action_name.lower() == "finish":
            return AgentAction(
                thought=self._extract_thought(text),
                action="finish",
                action_input=action_input,
                is_final=True,
                final_answer=action_input,
            )

        return AgentAction(
            thought=self._extract_thought(text),
            action=action_name,
            action_input=action_input,
            is_final=False,
        )

    def _extract_thought(self, text: str) -> str:
        match = self._THOUGHT_RE.search(text)
        return match.group(1).strip() if match else ""
