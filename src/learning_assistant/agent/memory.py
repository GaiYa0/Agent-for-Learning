"""Conversation memory — manages message history for the agent."""

from learning_assistant.models.chat import ChatMessage, MessageRole


class ConversationMemory:
    """Short-term message memory with optional compression interface."""

    def __init__(self, max_messages: int = 50) -> None:
        self._messages: list[ChatMessage] = []
        self._max_messages = max_messages

    def add_user_message(self, content: str) -> ChatMessage:
        msg = ChatMessage(role=MessageRole.USER, content=content)
        self._messages.append(msg)
        self._trim()
        return msg

    def add_assistant_message(self, content: str) -> ChatMessage:
        msg = ChatMessage(role=MessageRole.ASSISTANT, content=content)
        self._messages.append(msg)
        self._trim()
        return msg

    def add_tool_message(self, content: str, tool_call_id: str = "") -> ChatMessage:
        msg = ChatMessage(
            role=MessageRole.TOOL, content=content, tool_call_id=tool_call_id
        )
        self._messages.append(msg)
        self._trim()
        return msg

    def get_messages(self) -> list[ChatMessage]:
        return list(self._messages)

    def get_history_dicts(self) -> list[dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self._messages]

    def clear(self) -> None:
        self._messages.clear()

    def message_count(self) -> int:
        return len(self._messages)

    def _trim(self) -> None:
        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages :]
