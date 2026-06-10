"""Prompt builder — assembles multi-part prompts for the LLM."""

from dataclasses import dataclass, field

from learning_assistant.models.chat import ChatMessage


@dataclass
class PromptContext:
    """Holds all the pieces that can go into a prompt."""

    system: str = ""
    user: str = ""
    history: list[ChatMessage] = field(default_factory=list)
    tool_context: str = ""
    search_context: str = ""
    document_context: str = ""


class PromptBuilder:
    """Builds a complete prompt from context parts."""

    def build(self, ctx: PromptContext) -> str:
        parts: list[str] = []
        if ctx.system:
            parts.append(f"[System]\n{ctx.system}")
        if ctx.document_context:
            parts.append(f"[Document Context]\n{ctx.document_context}")
        if ctx.search_context:
            parts.append(f"[Search Results]\n{ctx.search_context}")
        if ctx.tool_context:
            parts.append(f"[Tool Results]\n{ctx.tool_context}")
        if ctx.history:
            history_text = self._format_history(ctx.history)
            parts.append(f"[Conversation History]\n{history_text}")
        if ctx.user:
            parts.append(f"[User]\n{ctx.user}")
        return "\n\n".join(parts)

    def _format_history(self, messages: list[ChatMessage]) -> str:
        lines: list[str] = []
        for msg in messages:
            lines.append(f"{msg.role}: {msg.content}")
        return "\n".join(lines)
