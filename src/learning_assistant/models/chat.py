"""Chat message and conversation models."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import Field

from learning_assistant.models.base import DomainModel


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ChatMessage(DomainModel):
    """A single message in a conversation."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tool_call_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Conversation(DomainModel):
    """An ordered collection of chat messages."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    messages: list[ChatMessage] = Field(default_factory=list)
    document_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def add_message(self, message: ChatMessage) -> None:
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

    def last_message(self) -> ChatMessage | None:
        return self.messages[-1] if self.messages else None

    def message_count(self) -> int:
        return len(self.messages)
