"""Search page — web search with results display."""

import asyncio

from learning_assistant.frontend.components.search_panel import (
    render_search_panel,
    render_search_results,
)
from learning_assistant.frontend.i18n.strings import UIStrings
from learning_assistant.frontend.services.api_client import APIClient


def render_search_page(api: APIClient, t: UIStrings) -> None:
    import streamlit as st

    result = render_search_panel(t)
    if not result:
        return

    query, max_results = result
    with st.spinner(t.search_searching):
        try:
            resp = asyncio.run(api.search(query, max_results))
            data = resp.get("data", {})
            results = data.get("results", [])
            render_search_results(results)
        except Exception as e:
            st.error(t.format_search_failed(str(e)))
