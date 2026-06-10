"""Tests for PDFDocument and DocumentChunk models."""

import pytest
from pydantic import ValidationError

from learning_assistant.models.document import DocumentChunk, PDFDocument


class TestPDFDocument:
    def test_create_with_valid_data(self) -> None:
        doc = PDFDocument(
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size=1024,
            page_count=10,
            content_hash="abc123",
        )
        assert doc.filename == "test.pdf"
        assert doc.page_count == 10
        assert doc.id is not None
        assert doc.created_at is not None

    def test_defaults(self) -> None:
        doc = PDFDocument(
            filename="a.pdf",
            file_path="/a",
            file_size=100,
            page_count=1,
            content_hash="h",
        )
        assert doc.title is None
        assert doc.author is None
        assert doc.metadata == {}

    def test_optional_fields(self) -> None:
        doc = PDFDocument(
            filename="a.pdf",
            file_path="/a",
            file_size=100,
            page_count=1,
            content_hash="h",
            title="My PDF",
            author="Author",
        )
        assert doc.title == "My PDF"
        assert doc.author == "Author"

    def test_empty_filename_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PDFDocument(
                filename="",
                file_path="/a",
                file_size=100,
                page_count=1,
                content_hash="h",
            )

    def test_zero_file_size_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PDFDocument(
                filename="a.pdf",
                file_path="/a",
                file_size=0,
                page_count=1,
                content_hash="h",
            )

    def test_negative_page_count_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PDFDocument(
                filename="a.pdf",
                file_path="/a",
                file_size=100,
                page_count=0,
                content_hash="h",
            )

    def test_extra_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PDFDocument(
                filename="a.pdf",
                file_path="/a",
                file_size=100,
                page_count=1,
                content_hash="h",
                unknown_field="bad",
            )

    def test_serialization(self) -> None:
        doc = PDFDocument(
            filename="a.pdf",
            file_path="/a",
            file_size=100,
            page_count=1,
            content_hash="h",
        )
        data = doc.model_dump()
        assert data["filename"] == "a.pdf"
        assert "id" in data

    def test_deserialization(self) -> None:
        data = {
            "filename": "a.pdf",
            "file_path": "/a",
            "file_size": 100,
            "page_count": 1,
            "content_hash": "h",
        }
        doc = PDFDocument.model_validate(data)
        assert doc.filename == "a.pdf"


class TestDocumentChunk:
    def test_create_with_valid_data(self) -> None:
        chunk = DocumentChunk(
            document_id="doc-1",
            content="Hello world",
            page_number=1,
            chunk_index=0,
            start_char=0,
            end_char=11,
        )
        assert chunk.content == "Hello world"
        assert chunk.embedding is None

    def test_embedding_field(self) -> None:
        chunk = DocumentChunk(
            document_id="doc-1",
            content="text",
            page_number=1,
            chunk_index=0,
            start_char=0,
            end_char=4,
            embedding=[0.1, 0.2, 0.3],
        )
        assert len(chunk.embedding) == 3

    def test_empty_content_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DocumentChunk(
                document_id="doc-1",
                content="",
                page_number=1,
                chunk_index=0,
                start_char=0,
                end_char=0,
            )

    def test_end_char_lt_start_char_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DocumentChunk(
                document_id="doc-1",
                content="text",
                page_number=1,
                chunk_index=0,
                start_char=10,
                end_char=5,
            )

    def test_page_number_zero_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DocumentChunk(
                document_id="doc-1",
                content="text",
                page_number=0,
                chunk_index=0,
                start_char=0,
                end_char=4,
            )

    def test_negative_chunk_index_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DocumentChunk(
                document_id="doc-1",
                content="text",
                page_number=1,
                chunk_index=-1,
                start_char=0,
                end_char=4,
            )

    def test_serialization_roundtrip(self) -> None:
        chunk = DocumentChunk(
            document_id="doc-1",
            content="text",
            page_number=1,
            chunk_index=0,
            start_char=0,
            end_char=4,
        )
        data = chunk.model_dump()
        restored = DocumentChunk.model_validate(data)
        assert restored.content == chunk.content
        assert restored.id == chunk.id
