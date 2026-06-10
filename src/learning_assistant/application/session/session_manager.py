"""Session manager — manages user sessions."""

from uuid import uuid4

from learning_assistant.application.exceptions import SessionError
from learning_assistant.application.session.conversation_store import (
    ConversationRecord,
    ConversationStore,
)


class SessionManager:
    """Creates, retrieves, and deletes sessions."""

    def __init__(self, store: ConversationStore | None = None) -> None:
        self._store = store or ConversationStore()

    def create_session(self) -> str:
        session_id = str(uuid4())
        self._store.create(session_id)
        return session_id

    def get_session(self, session_id: str) -> ConversationRecord:
        record = self._store.get(session_id)
        if record is None:
            raise SessionError(f"Session not found: {session_id}")
        return record

    def delete_session(self, session_id: str) -> None:
        self._store.delete(session_id)

    def session_exists(self, session_id: str) -> bool:
        return self._store.exists(session_id)

    def get_store(self) -> ConversationStore:
        return self._store
