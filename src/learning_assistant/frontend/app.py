"""Main Streamlit application."""

import streamlit as st

from learning_assistant.frontend.components.sidebar import render_sidebar
from learning_assistant.frontend.config.ui_settings import UISettings
from learning_assistant.frontend.i18n import get_strings
from learning_assistant.frontend.services.api_client import APIClient
from learning_assistant.frontend.services.session_service import SessionService
from learning_assistant.frontend.views.chat import render_chat_page
from learning_assistant.frontend.views.rag_chat import render_rag_chat_page
from learning_assistant.frontend.views.search import render_search_page
from learning_assistant.frontend.views.settings import render_settings_page
from learning_assistant.frontend.views.upload import render_upload_page


def main() -> None:
    settings: UISettings = st.session_state.setdefault("ui_settings", UISettings())
    t = get_strings(settings.language)

    st.set_page_config(
        page_title=t.app_title,
        page_icon="📚",
        layout="wide",
    )

    api: APIClient = st.session_state.setdefault(
        "api_client",
        APIClient(base_url=settings.api_base_url, api_key=settings.api_key),
    )
    session_service: SessionService = st.session_state.setdefault(
        "session_service", SessionService()
    )

    session_id = render_sidebar(session_service, t)
    page = st.session_state.get("current_page", "chat")

    if page == "chat":
        if session_id:
            render_chat_page(api, session_id, t)
        else:
            st.info(t.chat_no_session)
    elif page == "rag_chat":
        if session_id:
            render_rag_chat_page(api, session_id, t)
        else:
            st.info(t.rag_no_session)
    elif page == "upload":
        render_upload_page(api, t)
    elif page == "search":
        render_search_page(api, t)
    elif page == "settings":
        render_settings_page(t)


if __name__ == "__main__":
    main()
