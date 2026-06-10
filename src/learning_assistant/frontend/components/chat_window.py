"""Chat window component — message display and input."""

from learning_assistant.frontend.i18n.strings import UIStrings
from learning_assistant.frontend.state.chat_state import ChatState


def render_chat_window(state: ChatState, t: UIStrings) -> str | None:
    """Render chat messages and return user input."""
    import streamlit as st

    for msg in state.messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)
            if msg.thinking:
                with st.expander(t.thinking_process):
                    st.text(msg.thinking)

    if state.is_loading:
        with st.chat_message("assistant"):
            st.write(t.chat_loading)

    if state.error:
        st.error(state.error)

    return st.chat_input(t.chat_input)
