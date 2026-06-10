"""Tests for UploadState."""

from learning_assistant.frontend.state.upload_state import UploadState


class TestUploadState:
    def test_default(self) -> None:
        state = UploadState()
        assert state.is_uploading is False
        assert state.uploaded_filename == ""
        assert state.chunks_indexed == 0
        assert state.error is None

    def test_reset(self) -> None:
        state = UploadState()
        state.is_uploading = True
        state.uploaded_filename = "test.pdf"
        state.chunks_indexed = 5
        state.error = "err"
        state.reset()
        assert state.is_uploading is False
        assert state.uploaded_filename == ""
        assert state.chunks_indexed == 0
        assert state.error is None
