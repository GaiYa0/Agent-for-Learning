"""Tests for frontend component logic — no Streamlit runtime needed."""

from learning_assistant.frontend.services.session_service import SessionService
from learning_assistant.frontend.state.chat_state import ChatState
from learning_assistant.frontend.state.rag_state import RAGState


class TestChatStateExtended:
    def test_multiple_messages(self) -> None:
        state = ChatState()
        state.add_user_message("Q1")
        state.add_assistant_message("A1")
        state.add_user_message("Q2")
        state.add_assistant_message("A2")
        assert len(state.messages) == 4
        assert state.messages[0].role == "user"
        assert state.messages[3].role == "assistant"

    def test_error_clears_on_new_message(self) -> None:
        state = ChatState()
        state.set_error("old error")
        state.add_user_message("new")
        assert state.error == "old error"


class TestRAGStateExtended:
    def test_citations_from_dict(self) -> None:
        state = RAGState()
        state.set_citations([
            {"source": "doc.pdf", "page": "5", "snippet": "text1"},
            {"source": "web.com", "page": "0", "snippet": "text2"},
        ])
        assert state.citations[0].index == 1
        assert state.citations[0].page == 5
        assert state.citations[1].index == 2

    def test_empty_citations(self) -> None:
        state = RAGState()
        state.set_citations([])
        assert state.citations == []


class TestSessionServiceExtended:
    def test_default_name(self) -> None:
        svc = SessionService()
        session = svc.create_session()
        assert session.name.startswith("Session")

    def test_multiple_sessions(self) -> None:
        svc = SessionService()
        svc.create_session("A")
        svc.create_session("B")
        sessions = svc.list_sessions()
        assert len(sessions) == 2
        names = {s.name for s in sessions}
        assert {"A", "B"} == names
