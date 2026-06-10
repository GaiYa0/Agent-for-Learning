"""Tests for RAG domain models."""

import pytest
from pydantic import ValidationError

from learning_assistant.models.rag import (
    EmbeddingResult,
    RAGCitation,
    RAGResponse,
    RetrievedChunk,
    RetrievedContext,
)


class TestEmbeddingResult:
    def test_create_with_valid_data(self) -> None:
        result = EmbeddingResult(text="hello", embedding=[0.1, 0.2], model="test-model")
        assert result.text == "hello"
        assert len(result.embedding) == 2
        assert result.model == "test-model"


class TestRetrievedChunk:
    def test_create_with_valid_data(self) -> None:
        chunk = RetrievedChunk(content="text", score=0.9, chunk_id="c1", source="doc.pdf")
        assert chunk.page == 0
        assert chunk.score == 0.9

    def test_score_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RetrievedChunk(content="text", score=1.5)
        with pytest.raises(ValidationError):
            RetrievedChunk(content="text", score=-0.1)

    def test_negative_page_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RetrievedChunk(content="text", score=0.5, page=-1)


class TestRetrievedContext:
    def test_as_text_joins_chunks(self) -> None:
        ctx = RetrievedContext(
            chunks=[
                RetrievedChunk(content="A", score=1.0),
                RetrievedChunk(content="B", score=0.9),
            ],
            query="q",
        )
        assert ctx.as_text() == "A\n\nB"
        assert ctx.as_text(separator=" | ") == "A | B"

    def test_sources_deduplicates(self) -> None:
        ctx = RetrievedContext(
            chunks=[
                RetrievedChunk(content="A", score=1.0, source="doc.pdf"),
                RetrievedChunk(content="B", score=0.9, source="doc.pdf"),
                RetrievedChunk(content="C", score=0.8, source="web.com"),
            ],
        )
        assert ctx.sources() == ["doc.pdf", "web.com"]

    def test_sources_skips_empty(self) -> None:
        ctx = RetrievedContext(
            chunks=[
                RetrievedChunk(content="A", score=1.0, source=""),
                RetrievedChunk(content="B", score=0.9, source="doc.pdf"),
            ],
        )
        assert ctx.sources() == ["doc.pdf"]


class TestRAGCitation:
    def test_create_with_valid_data(self) -> None:
        cit = RAGCitation(
            index=1,
            source="doc.pdf",
            page=5,
            chunk_id="c1",
            snippet="snippet text",
        )
        assert cit.index == 1
        assert cit.page == 5

    def test_index_zero_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RAGCitation(index=0)

    def test_citation_alias_is_rag_citation(self) -> None:
        from learning_assistant.models.rag import Citation

        cit = Citation(index=1, source="doc.pdf")
        assert isinstance(cit, RAGCitation)


class TestRAGResponse:
    def test_create_with_valid_data(self) -> None:
        resp = RAGResponse(answer="The answer")
        assert resp.answer == "The answer"
        assert resp.citations == []
        assert resp.sources == []
        assert resp.retrieved_chunks == 0
        assert resp.retrieval_time_ms == 0
        assert resp.created_at is not None

    def test_negative_retrieval_time_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RAGResponse(answer="ok", retrieval_time_ms=-1)

    def test_with_citations(self) -> None:
        cit = RAGCitation(index=1, source="doc.pdf", snippet="text")
        resp = RAGResponse(answer="ok", citations=[cit], retrieved_chunks=1)
        assert len(resp.citations) == 1
        assert resp.citations[0].source == "doc.pdf"

    def test_serialization_roundtrip(self) -> None:
        resp = RAGResponse(answer="ok", sources=["doc.pdf"])
        data = resp.model_dump()
        restored = RAGResponse.model_validate(data)
        assert restored.answer == "ok"
        assert restored.sources == ["doc.pdf"]
