"""Citation prompt — adds source references to an answer."""

from learning_assistant.prompts.base import BasePromptTemplate

_TEMPLATE = """Given the following answer and sources, add numbered citations [1], [2], etc.

Answer:
{answer}

Sources:
{sources}

Rewrite the answer with inline citations. Keep the original meaning."""


class CitationPrompt(BasePromptTemplate):
    """Prompts the LLM to add citations to an answer."""

    def __init__(self, template: str | None = None) -> None:
        self._template = template or _TEMPLATE

    @property
    def name(self) -> str:
        return "citation"

    @property
    def version(self) -> str:
        return "v1"

    @property
    def required_variables(self) -> set[str]:
        return {"answer", "sources"}

    def build(self, **kwargs: str) -> str:
        return self._template.format(**kwargs)
