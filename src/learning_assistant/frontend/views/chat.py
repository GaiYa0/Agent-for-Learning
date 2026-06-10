"""Chat page — simple agent conversation."""

from learning_assistant.frontend.components.chat_window import render_chat_window
from learning_assistant.frontend.i18n.strings import UIStrings
from learning_assistant.frontend.services.api_client import APIClient
from learning_assistant.frontend.state.chat_state import ChatState


def render_chat_page(api: APIClient, session_id: str, t: UIStrings) -> None:
    import streamlit as st

    state_key = f"chat_state_{session_id}"
    state: ChatState = st.session_state.setdefault(state_key, ChatState())

    user_input = render_chat_window(state, t)
    if not user_input:
        return

    state.add_user_message(user_input)
    state.set_error(None)

    try:
        with st.chat_message("assistant"):
            full = st.write_stream(api.chat_stream(session_id, user_input))
        answer = full or api.last_stream_meta.get("answer") or t.err_no_response
        state.add_assistant_message(str(answer))
    except Exception as e:
        state.set_error(t.format_chat_stream_error(str(e)))
    finally:
        st.rerun()
