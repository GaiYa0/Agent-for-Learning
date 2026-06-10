"""Tests for SessionManager."""

import pytest

from learning_assistant.application.exceptions import SessionError
from learning_assistant.application.session.session_manager import SessionManager


@pytest.fixture()
def manager() -> SessionManager:
    return SessionManager()


class TestSessionManager:
    def test_create_session(self, manager: SessionManager) -> None:
        sid = manager.create_session()
        assert sid
        assert manager.session_exists(sid)

    def test_get_session(self, manager: SessionManager) -> None:
        sid = manager.create_session()
        record = manager.get_session(sid)
        assert record.session_id == sid

    def test_get_nonexistent_raises(self, manager: SessionManager) -> None:
        with pytest.raises(SessionError, match="not found"):
            manager.get_session("nonexistent")

    def test_delete_session(self, manager: SessionManager) -> None:
        sid = manager.create_session()
        manager.delete_session(sid)
        assert not manager.session_exists(sid)

    def test_delete_nonexistent_is_noop(self, manager: SessionManager) -> None:
        manager.delete_session("ghost")

    def test_get_store(self, manager: SessionManager) -> None:
        assert manager.get_store() is not None
