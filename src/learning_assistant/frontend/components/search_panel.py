"""Search panel component — web search input and results."""

from learning_assistant.frontend.i18n.strings import UIStrings


def render_search_panel(t: UIStrings) -> tuple[str, int] | None:
    """Render search form and return (query, max_results) if submitted."""
    import streamlit as st

    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(t.search_query)
    with col2:
        max_results = st.number_input(
            t.search_results_count, min_value=1, max_value=20, value=5
        )

    if st.button(t.search_button) and query:
        return query, max_results
    return None


def render_search_results(results: list[dict[str, str]]) -> None:
    import streamlit as st

    for r in results:
        with st.container():
            st.markdown(f"**{r.get('title', '')}**")
            st.caption(r.get("snippet", ""))
            st.markdown(f"[{r.get('url', '')}]({r.get('url', '')})")
            st.divider()
