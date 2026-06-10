"""In-memory conversation store."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from learning_assistant.models.chat import ChatMessage


class ConversationRecord(BaseModel):
    session_id: str
    messages: list[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConversationStore:
    """Stores conversations in memory."""

    def __init__(self) -> None:
        self._records: dict[str, ConversationRecord] = {}

    def get(self, session_id: str) -> ConversationRecord | None:
        return self._records.get(session_id)

    def create(self, session_id: str) -> ConversationRecord:
        record = ConversationRecord(session_id=session_id)
        self._records[session_id] = record
        return record

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        record = self._records.get(session_id)
        if record:
            record.messages.append(message)

    def delete(self, session_id: str) -> None:
        self._records.pop(session_id, None)

    def exists(self, session_id: str) -> bool:
        return session_id in self._records
