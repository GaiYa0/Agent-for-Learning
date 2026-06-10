"""Citation panel component — displays source references."""

from learning_assistant.frontend.i18n.strings import UIStrings
from learning_assistant.models.rag import RAGCitation


def render_citation_panel(citations: list[RAGCitation], t: UIStrings) -> None:
    import streamlit as st

    if not citations:
        return
    with st.expander(t.citation_sources):
        for cit in citations:
            parts = [f"[{cit.index}]"]
            if cit.source:
                parts.append(cit.source)
            if cit.page:
                parts.append(f"p.{cit.page}")
            st.markdown(" ".join(parts))
            if cit.snippet:
                st.caption(cit.snippet[:200])
