"""Tests for frontend modules with mocked Streamlit."""

import sys
from unittest.mock import MagicMock

import pytest

from learning_assistant.frontend.i18n import get_strings


@pytest.fixture()
def t():
    return get_strings("zh-CN")


@pytest.fixture(autouse=True)
def mock_streamlit() -> None:
    """Inject a mock streamlit module."""
    mock_st = MagicMock()
    mock_st.chat_input.return_value = None
    mock_st.chat_message.return_value.__enter__ = MagicMock()
    mock_st.chat_message.return_value.__exit__ = MagicMock()
    mock_st.expander.return_value.__enter__ = MagicMock()
    mock_st.expander.return_value.__exit__ = MagicMock()
    mock_st.sidebar.return_value.__enter__ = MagicMock()
    mock_st.sidebar.return_value.__exit__ = MagicMock()
    mock_st.spinner.return_value.__enter__ = MagicMock()
    mock_st.spinner.return_value.__exit__ = MagicMock()
    mock_st.columns.return_value = (MagicMock(), MagicMock())
    sys.modules["streamlit"] = mock_st


class TestChatWindow:
    def test_render_empty(self, t) -> None:
        from learning_assistant.frontend.components.chat_window import render_chat_window
        from learning_assistant.frontend.state.chat_state import ChatState

        state = ChatState()
        result = render_chat_window(state, t)
        assert result is None

    def test_render_with_messages(self, t) -> None:
        from learning_assistant.frontend.components.chat_window import render_chat_window
        from learning_assistant.frontend.state.chat_state import ChatState

        state = ChatState()
        state.add_user_message("Hello")
        state.add_assistant_message("Hi!")
        result = render_chat_window(state, t)
        assert result is None

    def test_render_loading(self, t) -> None:
        from learning_assistant.frontend.components.chat_window import render_chat_window
        from learning_assistant.frontend.state.chat_state import ChatState

        state = ChatState()
        state.set_loading(True)
        result = render_chat_window(state, t)
        assert result is None

    def test_render_error(self, t) -> None:
        from learning_assistant.frontend.components.chat_window import render_chat_window
        from learning_assistant.frontend.state.chat_state import ChatState

        state = ChatState()
        state.set_error("Something went wrong")
        result = render_chat_window(state, t)
        assert result is None


class TestCitationPanel:
    def test_render_empty(self, t) -> None:
        from learning_assistant.frontend.components.citation_panel import render_citation_panel
        render_citation_panel([], t)

    def test_render_with_citations(self, t) -> None:
        from learning_assistant.frontend.components.citation_panel import render_citation_panel
        from learning_assistant.models.rag import RAGCitation

        citations = [
            RAGCitation(index=1, source="doc.pdf", page=5, snippet="text"),
            RAGCitation(index=2, source="web.com", page=0),
        ]
        render_citation_panel(citations, t)


class TestMessageCard:
    def test_render_user(self, t) -> None:
        from learning_assistant.frontend.components.message_card import render_message_card
        render_message_card("user", "Hello", t=t)

    def test_render_assistant_with_thinking(self, t) -> None:
        from learning_assistant.frontend.components.message_card import render_message_card
        render_message_card("assistant", "Answer", thinking="I was thinking...", t=t)


class TestThinkingPanel:
    def test_render_empty(self, t) -> None:
        from learning_assistant.frontend.components.thinking_panel import render_thinking_panel
        render_thinking_panel("", t)

    def test_render_with_content(self, t) -> None:
        from learning_assistant.frontend.components.thinking_panel import render_thinking_panel
        render_thinking_panel(
            "Thought: I need to search\nAction: search\nAction Input: query\n"
            "Observation: Found results\nFinal Answer: The answer is 42.",
            t,
        )


class TestUploadPanel:
    def test_render_no_upload(self, t) -> None:
        import streamlit as st

        from learning_assistant.frontend.components.upload_panel import render_upload_panel
        from learning_assistant.frontend.state.upload_state import UploadState
        st.file_uploader.return_value = None
        state = UploadState()
        result = render_upload_panel(state, t)
        assert result is None

    def test_render_with_success(self, t) -> None:
        import streamlit as st

        from learning_assistant.frontend.components.upload_panel import render_upload_panel
        from learning_assistant.frontend.state.upload_state import UploadState
        st.file_uploader.return_value = None
        state = UploadState()
        state.uploaded_filename = "test.pdf"
        state.chunks_indexed = 5
        result = render_upload_panel(state, t)
        assert result is None

    def test_render_with_error(self, t) -> None:
        import streamlit as st

        from learning_assistant.frontend.components.upload_panel import render_upload_panel
        from learning_assistant.frontend.state.upload_state import UploadState
        st.file_uploader.return_value = None
        state = UploadState()
        state.error = "Upload failed"
        result = render_upload_panel(state, t)
        assert result is None


class TestSearchPanel:
    def test_render_no_input(self, t) -> None:
        import streamlit as st

        from learning_assistant.frontend.components.search_panel import render_search_panel
        st.text_input.return_value = ""
        result = render_search_panel(t)
        assert result is None


class TestSettingsPage:
    def test_render(self, t) -> None:
        import streamlit as st

        from learning_assistant.frontend.config.ui_settings import UISettings
        from learning_assistant.frontend.views.settings import render_settings_page

        st.session_state = {"ui_settings": UISettings()}
        st.selectbox.side_effect = ["简体中文", "浅色"]
        render_settings_page(t)


class TestSidebar:
    def test_render(self, t) -> None:
        import streamlit as st

        from learning_assistant.frontend.components.sidebar import render_sidebar
        from learning_assistant.frontend.services.session_service import SessionService
        mock_state: dict[str, object] = {"current_page": "chat"}
        st.session_state = mock_state
        svc = SessionService()
        result = render_sidebar(svc, t)
        assert result is None
        st.radio.assert_called_once()
        call_kwargs = st.radio.call_args.kwargs
        assert call_kwargs["key"] == "current_page"
        assert "index" not in call_kwargs
