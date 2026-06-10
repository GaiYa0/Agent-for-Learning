"""Tests for frontend page logic — mocked Streamlit."""


from learning_assistant.frontend.config.ui_settings import UISettings
from learning_assistant.frontend.services.api_client import APIClient
from learning_assistant.frontend.services.session_service import SessionService
from learning_assistant.frontend.state.chat_state import ChatState
from learning_assistant.frontend.state.rag_state import RAGState
from learning_assistant.frontend.state.upload_state import UploadState


class TestUISettingsExtended:
    def test_all_defaults(self) -> None:
        s = UISettings()
        assert s.language == "zh-CN"
        assert s.api_base_url == "http://localhost:8000"
        assert s.default_top_k == 5
        assert s.default_temperature == 0.2
        assert s.theme == "light"
        assert s.max_history == 50

    def test_custom_values(self) -> None:
        s = UISettings(
            api_base_url="http://custom:9000",
            default_top_k=10,
            default_temperature=0.5,
            theme="dark",
            max_history=100,
        )
        assert s.api_base_url == "http://custom:9000"
        assert s.default_top_k == 10
        assert s.default_temperature == 0.5
        assert s.theme == "dark"
        assert s.max_history == 100


class TestSessionServiceExtended:
    def test_create_and_list(self) -> None:
        svc = SessionService()
        svc.create_session("A")
        svc.create_session("B")
        assert len(svc.list_sessions()) == 2

    def test_add_message_to_session(self) -> None:
        svc = SessionService()
        session = svc.create_session()
        svc.add_message(session.id, "user", "Hello")
        messages = svc.get_messages(session.id)
        assert len(messages) == 1
        assert messages[0]["role"] == "user"

    def test_delete_session(self) -> None:
        svc = SessionService()
        session = svc.create_session()
        svc.delete_session(session.id)
        assert svc.get_session(session.id) is None


class TestChatStateExtended:
    def test_full_conversation(self) -> None:
        state = ChatState()
        state.add_user_message("Q1")
        state.add_assistant_message("A1", thinking="thinking")
        state.add_user_message("Q2")
        state.add_assistant_message("A2")
        assert len(state.messages) == 4
        assert state.messages[1].thinking == "thinking"

    def test_error_handling(self) -> None:
        state = ChatState()
        state.set_error("error")
        assert state.error == "error"
        state.clear()
        assert state.error is None


class TestRAGStateExtended:
    def test_citations(self) -> None:
        state = RAGState()
        state.set_citations([{"source": "doc.pdf", "page": "5", "snippet": "text"}])
        assert len(state.citations) == 1
        assert state.citations[0].source == "doc.pdf"

    def test_clear_resets_citations(self) -> None:
        state = RAGState()
        state.set_citations([{"source": "a", "page": "1"}])
        state.retrieved_chunks = 5
        state.clear()
        assert state.citations == []
        assert state.retrieved_chunks == 0


class TestUploadStateExtended:
    def test_full_cycle(self) -> None:
        state = UploadState()
        state.is_uploading = True
        state.uploaded_filename = "test.pdf"
        state.chunks_indexed = 10
        assert state.is_uploading is True
        state.reset()
        assert state.is_uploading is False
        assert state.uploaded_filename == ""
        assert state.chunks_indexed == 0


class TestAPIClientMethods:
    def test_init(self) -> None:
        client = APIClient(base_url="http://test:8000", timeout=10.0)
        assert client.base_url == "http://test:8000"
        assert client.timeout == 10.0

    def test_default_init(self) -> None:
        client = APIClient()
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 30.0
