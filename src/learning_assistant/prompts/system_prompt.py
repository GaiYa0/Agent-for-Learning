"""System prompt — defines agent persona and behaviour rules."""

from learning_assistant.prompts.base import BasePromptTemplate

_DEFAULT_TEMPLATE = """You are a learning assistant AI. Your role is to help students understand course materials.

## Rules
- Answer questions based on the provided course materials first.
- If the answer is not in the materials, use web search and clearly state the source.
- Always cite your sources with numbered references [1], [2], etc.
- Be concise, accurate, and educational.

{custom_instructions}"""


class SystemPrompt(BasePromptTemplate):
    """Configurable system prompt for the learning assistant agent."""

    def __init__(self, template: str | None = None) -> None:
        self._template = template or _DEFAULT_TEMPLATE

    @property
    def name(self) -> str:
        return "system"

    @property
    def version(self) -> str:
        return "v1"

    @property
    def required_variables(self) -> set[str]:
        return {"custom_instructions"}

    def build(self, **kwargs: str) -> str:
        return self._template.format(**kwargs)
