"""Tests for SessionService."""

from learning_assistant.frontend.services.session_service import SessionService


class TestSessionService:
    def test_create_session(self) -> None:
        svc = SessionService()
        session = svc.create_session("Test")
        assert session.name == "Test"
        assert session.id

    def test_get_session(self) -> None:
        svc = SessionService()
        session = svc.create_session()
        assert svc.get_session(session.id) is session

    def test_get_nonexistent(self) -> None:
        svc = SessionService()
        assert svc.get_session("nope") is None

    def test_list_sessions(self) -> None:
        svc = SessionService()
        svc.create_session("A")
        svc.create_session("B")
        sessions = svc.list_sessions()
        assert len(sessions) == 2

    def test_delete_session(self) -> None:
        svc = SessionService()
        session = svc.create_session()
        svc.delete_session(session.id)
        assert svc.get_session(session.id) is None

    def test_delete_nonexistent(self) -> None:
        svc = SessionService()
        svc.delete_session("ghost")

    def test_add_message(self) -> None:
        svc = SessionService()
        session = svc.create_session()
        svc.add_message(session.id, "user", "Hello")
        svc.add_message(session.id, "assistant", "Hi!")
        messages = svc.get_messages(session.id)
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

    def test_get_messages_nonexistent(self) -> None:
        svc = SessionService()
        assert svc.get_messages("nope") == []
