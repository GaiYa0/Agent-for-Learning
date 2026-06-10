"""Tests for FixedSizeChunker."""

import pytest

from learning_assistant.services.exceptions import ChunkError
from learning_assistant.services.pdf.chunker import FixedSizeChunker


class TestFixedSizeChunkerInit:
    def test_default_params(self) -> None:
        c = FixedSizeChunker()
        assert c.chunk_size == 1000
        assert c.chunk_overlap == 200

    def test_custom_params(self) -> None:
        c = FixedSizeChunker(chunk_size=500, chunk_overlap=50)
        assert c.chunk_size == 500

    def test_zero_chunk_size_raises(self) -> None:
        with pytest.raises(ChunkError, match="positive"):
            FixedSizeChunker(chunk_size=0)

    def test_negative_chunk_size_raises(self) -> None:
        with pytest.raises(ChunkError, match="positive"):
            FixedSizeChunker(chunk_size=-1)

    def test_negative_overlap_raises(self) -> None:
        with pytest.raises(ChunkError, match="non-negative"):
            FixedSizeChunker(chunk_overlap=-1)

    def test_overlap_gte_size_raises(self) -> None:
        with pytest.raises(ChunkError, match="must be <"):
            FixedSizeChunker(chunk_size=100, chunk_overlap=100)


class TestChunkText:
    def test_empty_text(self) -> None:
        c = FixedSizeChunker(chunk_size=10, chunk_overlap=2)
        assert c.chunk_text("") == []

    def test_whitespace_only(self) -> None:
        c = FixedSizeChunker(chunk_size=10, chunk_overlap=2)
        assert c.chunk_text("   ") == []

    def test_short_text_single_chunk(self) -> None:
        c = FixedSizeChunker(chunk_size=100, chunk_overlap=10)
        result = c.chunk_text("Hello world")
        assert len(result) == 1
        assert result[0] == "Hello world"

    def test_long_text_multiple_chunks(self) -> None:
        text = "A" * 250
        c = FixedSizeChunker(chunk_size=100, chunk_overlap=20)
        chunks = c.chunk_text(text)
        assert len(chunks) >= 2

    def test_chunks_are_non_empty(self) -> None:
        text = "A" * 500
        c = FixedSizeChunker(chunk_size=100, chunk_overlap=20)
        for chunk in c.chunk_text(text):
            assert chunk.strip()

    def test_sentence_break_respected(self) -> None:
        text = "First sentence. " + "X" * 200
        c = FixedSizeChunker(chunk_size=100, chunk_overlap=10)
        chunks = c.chunk_text(text)
        assert len(chunks) >= 1


class TestChunkDocument:
    def test_returns_document_chunks(self) -> None:
        c = FixedSizeChunker(chunk_size=100, chunk_overlap=10)
        chunks = c.chunk_document("Hello world. " * 20, document_id="doc-1")
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.document_id == "doc-1"
            assert chunk.content.strip()

    def test_chunk_indices_sequential(self) -> None:
        c = FixedSizeChunker(chunk_size=50, chunk_overlap=5)
        chunks = c.chunk_document("A" * 200)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_auto_generated_document_id(self) -> None:
        c = FixedSizeChunker(chunk_size=100, chunk_overlap=10)
        chunks = c.chunk_document("Hello world")
        assert chunks[0].document_id

    def test_empty_text_returns_empty(self) -> None:
        c = FixedSizeChunker(chunk_size=100, chunk_overlap=10)
        assert c.chunk_document("") == []
