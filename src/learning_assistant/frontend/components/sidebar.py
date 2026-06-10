"""Sidebar component — session list, navigation, settings."""

from learning_assistant.frontend.i18n import PAGE_KEYS
from learning_assistant.frontend.i18n.strings import UIStrings
from learning_assistant.frontend.services.session_service import SessionService


def render_sidebar(session_service: SessionService, t: UIStrings) -> str | None:
    """Render sidebar and return selected session ID."""
    import streamlit as st

    with st.sidebar:
        st.title(t.app_title)
        st.divider()

        if st.button(t.btn_new_chat, use_container_width=True):
            session = session_service.create_session()
            session.name = t.format_session_name(session_id=session.id)
            st.session_state["active_session"] = session.id
            st.rerun()

        st.subheader(t.nav_sessions)
        sessions = session_service.list_sessions()
        for session in sessions:
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(session.name, key=f"sel_{session.id}", use_container_width=True):
                    st.session_state["active_session"] = session.id
                    st.rerun()
            with col2:
                if st.button("X", key=f"del_{session.id}"):
                    session_service.delete_session(session.id)
                    if st.session_state.get("active_session") == session.id:
                        st.session_state["active_session"] = None
                    st.rerun()

        st.divider()
        if (
            "current_page" not in st.session_state
            or st.session_state["current_page"] not in PAGE_KEYS
        ):
            st.session_state["current_page"] = PAGE_KEYS[0]

        st.radio(
            "Navigation",
            PAGE_KEYS,
            key="current_page",
            format_func=t.page_label,
            label_visibility="collapsed",
        )

    return st.session_state.get("active_session")
