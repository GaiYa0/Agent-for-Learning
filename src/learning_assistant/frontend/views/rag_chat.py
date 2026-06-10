"""RAG Chat page — retrieval-augmented conversation."""

from learning_assistant.frontend.components.chat_window import render_chat_window
from learning_assistant.frontend.components.citation_panel import render_citation_panel
from learning_assistant.frontend.config.ui_settings import UISettings
from learning_assistant.frontend.i18n.strings import UIStrings
from learning_assistant.frontend.services.api_client import APIClient
from learning_assistant.frontend.state.rag_state import RAGState


def render_rag_chat_page(api: APIClient, session_id: str, t: UIStrings) -> None:
    import streamlit as st

    state_key = f"rag_state_{session_id}"
    state: RAGState = st.session_state.setdefault(state_key, RAGState())
    settings: UISettings = st.session_state.get("ui_settings", UISettings())

    user_input = render_chat_window(state, t)
    if not user_input:
        render_citation_panel(state.citations, t)
        return

    state.add_user_message(user_input)
    state.set_error(None)

    try:
        with st.chat_message("assistant"):
            full = st.write_stream(
                api.chat_stream(
                    session_id,
                    user_input,
                    use_rag=True,
                    top_k=settings.default_top_k,
                )
            )
        meta = api.last_stream_meta
        answer = full or meta.get("answer") or t.err_no_response
        citations = meta.get("citations", [])
        metadata = meta.get("metadata") or {}
        state.add_assistant_message(str(answer), citations=citations)
        state.set_citations(citations)
        state.retrieval_time_ms = int(metadata.get("retrieval_time_ms", 0))
        state.retrieved_chunks = len(citations)
    except Exception as e:
        state.set_error(t.format_chat_stream_error(str(e)))
    finally:
        st.rerun()
