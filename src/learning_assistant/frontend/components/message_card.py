"""Message card component — renders a single chat message."""

from learning_assistant.frontend.i18n.strings import UIStrings


def render_message_card(
    role: str, content: str, thinking: str = "", *, t: UIStrings
) -> None:
    import streamlit as st

    with st.chat_message(role):
        st.markdown(content)
        if thinking:
            with st.expander(t.thinking_process):
                st.text(thinking)
