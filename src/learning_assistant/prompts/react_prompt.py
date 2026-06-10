"""ReAct prompt — guides the agent through Thought/Action/Observation loops."""

from learning_assistant.prompts.base import BasePromptTemplate

_TEMPLATE = """Answer the following question using the ReAct reasoning pattern.

Question: {question}

{context}Available tools:
{tools}

Respond in exactly this format:

Thought: <your reasoning about what to do next>
Action: <tool name or "finish">
Action Input: <input for the tool, or your final answer>

Previous observations:
{observations}"""


class ReActPrompt(BasePromptTemplate):
    """Produces a ReAct-formatted prompt for multi-step reasoning."""

    def __init__(self, template: str | None = None) -> None:
        self._template = template or _TEMPLATE

    @property
    def name(self) -> str:
        return "react"

    @property
    def version(self) -> str:
        return "v1"

    @property
    def required_variables(self) -> set[str]:
        return {"question", "tools", "observations", "context"}

    def build(self, **kwargs: str) -> str:
        context = kwargs.get("context", "")
        if context and not context.endswith("\n"):
            context = f"{context}\n"
        kwargs["context"] = context
        return self._template.format(**kwargs)
