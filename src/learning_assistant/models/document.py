"""PDF document and chunk models."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import Field, ValidationInfo, field_validator

from learning_assistant.models.base import DomainModel


class DocumentChunk(DomainModel):
    """A text chunk extracted from a PDF document."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    content: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    chunk_index: int = Field(ge=0)
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    embedding: list[float] | None = None

    @field_validator("end_char")
    @classmethod
    def end_char_gte_start_char(cls, v: int, info: ValidationInfo) -> int:
        start = info.data.get("start_char", 0)
        if v < start:
            msg = f"end_char ({v}) must be >= start_char ({start})"
            raise ValueError(msg)
        return v


class PDFDocument(DomainModel):
    """Represents an uploaded PDF document."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str = Field(min_length=1)
    file_path: str = Field(min_length=1)
    file_size: int = Field(gt=0)
    page_count: int = Field(ge=1)
    title: str | None = None
    author: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    content_hash: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
