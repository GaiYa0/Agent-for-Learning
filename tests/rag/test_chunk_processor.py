"""Tests for ChunkProcessor — offline only."""

import pytest

from learning_assistant.rag.exceptions import IndexingError
from learning_assistant.rag.indexing.chunk_processor import ChunkProcessor


class TestChunkProcessorInit:
    def test_defaults(self) -> None:
        c = ChunkProcessor()
        assert c._chunk_size == 1000
        assert c._chunk_overlap == 200

    def test_zero_size_raises(self) -> None:
        with pytest.raises(IndexingError):
            ChunkProcessor(chunk_size=0)

    def test_negative_overlap_raises(self) -> None:
        with pytest.raises(IndexingError):
            ChunkProcessor(chunk_overlap=-1)

    def test_overlap_gte_size_raises(self) -> None:
        with pytest.raises(IndexingError):
            ChunkProcessor(chunk_size=100, chunk_overlap=100)


class TestChunkProcessorProcess:
    def test_empty_text(self) -> None:
        c = ChunkProcessor(chunk_size=100, chunk_overlap=10)
        assert c.process("") == []

    def test_short_text(self) -> None:
        c = ChunkProcessor(chunk_size=1000, chunk_overlap=100)
        chunks = c.process("Hello world.")
        assert len(chunks) == 1
        assert chunks[0].content == "Hello world."

    def test_long_text(self) -> None:
        c = ChunkProcessor(chunk_size=100, chunk_overlap=10)
        text = "A" * 500
        chunks = c.process(text)
        assert len(chunks) > 1

    def test_chunk_indices(self) -> None:
        c = ChunkProcessor(chunk_size=50, chunk_overlap=5)
        chunks = c.process("A" * 200)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_document_id(self) -> None:
        c = ChunkProcessor(chunk_size=100, chunk_overlap=10)
        chunks = c.process("Hello world.", document_id="doc-1")
        assert all(ch.document_id == "doc-1" for ch in chunks)
