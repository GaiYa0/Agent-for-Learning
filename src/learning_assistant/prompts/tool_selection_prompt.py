"""Tool selection prompt — helps the agent choose the right tool."""

from learning_assistant.prompts.base import BasePromptTemplate

_TEMPLATE = """Given the user's question and the available tools, select the most appropriate tool.

Question: {question}

Available tools:
{tools}

Respond with ONLY a JSON object:
{{"tool": "<tool_name>", "reason": "<brief explanation>"}}"""


class ToolSelectionPrompt(BasePromptTemplate):
    """Prompts the LLM to select a tool for a given question."""

    def __init__(self, template: str | None = None) -> None:
        self._template = template or _TEMPLATE

    @property
    def name(self) -> str:
        return "tool_selection"

    @property
    def version(self) -> str:
        return "v1"

    @property
    def required_variables(self) -> set[str]:
        return {"question", "tools"}

    def build(self, **kwargs: str) -> str:
        return self._template.format(**kwargs)
