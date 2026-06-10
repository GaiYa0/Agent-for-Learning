"""Tests for CitationPipeline — offline only."""

from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.pipelines.citation_pipeline import CitationPipeline


class TestCitationPipeline:
    def test_build_citations(self) -> None:
        chunks = [
            RetrievedChunk(content="A", score=0.9, source="doc.pdf", page=1, chunk_id="c1"),
            RetrievedChunk(content="B", score=0.8, source="web", page=0, chunk_id="c2"),
        ]
        pipeline = CitationPipeline()
        citations = pipeline.build_citations(chunks)
        assert len(citations) == 2
        assert citations[0].index == 1
        assert citations[0].source == "doc.pdf"
        assert citations[1].index == 2

    def test_format_citations(self) -> None:
        chunks = [
            RetrievedChunk(content="A", score=0.9, source="doc.pdf", page=5, chunk_id="c1"),
        ]
        pipeline = CitationPipeline()
        citations = pipeline.build_citations(chunks)
        formatted = pipeline.format_citations(citations)
        assert "[1]" in formatted
        assert "doc.pdf" in formatted
        assert "p.5" in formatted

    def test_empty(self) -> None:
        pipeline = CitationPipeline()
        citations = pipeline.build_citations([])
        assert citations == []
        assert pipeline.format_citations([]) == ""
