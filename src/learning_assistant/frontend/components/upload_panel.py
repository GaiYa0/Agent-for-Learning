"""Upload panel component — file upload with progress."""

from learning_assistant.frontend.i18n.strings import UIStrings
from learning_assistant.frontend.state.upload_state import UploadState


def render_upload_panel(
    state: UploadState, t: UIStrings
) -> tuple[str, bytes] | None:
    """Render upload form and return (filename, content) if uploaded."""
    import streamlit as st

    uploaded = st.file_uploader(t.upload_document, type=["txt", "pdf"])
    if uploaded and st.button(t.upload_and_index):
        return uploaded.name, uploaded.read()

    if state.is_uploading:
        st.info(t.upload_indexing)

    if state.uploaded_filename:
        st.success(
            t.format_upload_indexed(state.uploaded_filename, state.chunks_indexed)
        )

    if state.error:
        st.error(state.error)

    return None
