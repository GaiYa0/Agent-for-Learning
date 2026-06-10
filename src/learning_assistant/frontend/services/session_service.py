"""Session service — manages user sessions in Streamlit session state."""

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Session:
    id: str
    name: str
    messages: list[dict[str, str]] = field(default_factory=list)


class SessionService:
    """Manages chat sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create_session(self, name: str = "") -> Session:
        session_id = str(uuid4())[:8]
        session = Session(id=session_id, name=name or f"Session {session_id}")
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[Session]:
        return list(self._sessions.values())

    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def add_message(
        self, session_id: str, role: str, content: str
    ) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.messages.append({"role": role, "content": content})

    def get_messages(self, session_id: str) -> list[dict[str, str]]:
        session = self._sessions.get(session_id)
        return session.messages if session else []
