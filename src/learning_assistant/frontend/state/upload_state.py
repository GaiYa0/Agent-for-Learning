"""Upload state — manages file upload UI state."""

from dataclasses import dataclass


@dataclass
class UploadState:
    is_uploading: bool = False
    uploaded_filename: str = ""
    chunks_indexed: int = 0
    error: str | None = None

    def reset(self) -> None:
        self.is_uploading = False
        self.uploaded_filename = ""
        self.chunks_indexed = 0
        self.error = None
