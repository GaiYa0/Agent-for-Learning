"""Upload page — document upload and indexing."""

import asyncio

from learning_assistant.frontend.components.upload_panel import render_upload_panel
from learning_assistant.frontend.i18n.strings import UIStrings
from learning_assistant.frontend.services.api_client import APIClient
from learning_assistant.frontend.state.upload_state import UploadState


def render_upload_page(api: APIClient, t: UIStrings) -> None:
    import streamlit as st

    state: UploadState = st.session_state.setdefault("upload_state", UploadState())

    result = render_upload_panel(state, t)
    if not result:
        return

    filename, content = result
    state.is_uploading = True
    state.error = None

    try:
        resp = asyncio.run(api.upload(filename, content))
        data = resp.get("data", {})
        state.uploaded_filename = data.get("filename", filename)
        state.chunks_indexed = data.get("chunks_indexed", 0)
    except Exception as e:
        state.error = str(e)
    finally:
        state.is_uploading = False
        st.rerun()
