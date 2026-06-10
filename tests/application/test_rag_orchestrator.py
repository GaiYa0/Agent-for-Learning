"""Tests for RAGOrchestrator."""

import pytest

from learning_assistant.application.orchestrators.rag_orchestrator import RAGOrchestrator
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.pipelines.citation_pipeline import CitationPipeline
from learning_assistant.rag.pipelines.retrieval_pipeline import RetrievalPipeline
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


@pytest.fixture()
async def orchestrator() -> RAGOrchestrator:
    emb = MockEmbeddingProvider(dim=64)
    store = InMemoryVectorStore()
    retriever = SimilarityRetriever(emb, store)
    pipeline = RetrievalPipeline(retriever)
    return RAGOrchestrator(emb, store, pipeline)


class TestRAGOrchestrator:
    @pytest.mark.asyncio
    async def test_retrieve(self, orchestrator: RAGOrchestrator) -> None:
        ctx = await orchestrator.retrieve("test")
        assert ctx.retrieval_time_ms >= 0

    @pytest.mark.asyncio
    async def test_index_text(self, orchestrator: RAGOrchestrator) -> None:
        count = await orchestrator.index_text("Hello world. " * 100)
        assert count > 0

    def test_get_citation_pipeline(self, orchestrator: RAGOrchestrator) -> None:
        assert isinstance(orchestrator.get_citation_pipeline(), CitationPipeline)
