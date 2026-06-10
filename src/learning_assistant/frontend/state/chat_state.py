"""Chat state — manages chat UI state."""

from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    role: str
    content: str
    thinking: str = ""
    citations: list[dict[str, str]] = field(default_factory=list)


@dataclass
class ChatState:
    messages: list[ChatMessage] = field(default_factory=list)
    is_loading: bool = False
    error: str | None = None

    def add_user_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="user", content=content))

    def add_assistant_message(
        self, content: str, thinking: str = "", citations: list[dict[str, str]] | None = None
    ) -> None:
        self.messages.append(
            ChatMessage(role="assistant", content=content, thinking=thinking, citations=citations or [])
        )

    def clear(self) -> None:
        self.messages.clear()
        self.is_loading = False
        self.error = None

    def set_loading(self, loading: bool) -> None:
        self.is_loading = loading

    def set_error(self, error: str | None) -> None:
        self.error = error
