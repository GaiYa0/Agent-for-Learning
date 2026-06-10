"""Tests for RetrievalPipeline — offline only."""

import pytest

from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.pipelines.retrieval_pipeline import RetrievalPipeline
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


@pytest.mark.asyncio
async def test_retrieval_pipeline() -> None:
    emb = MockEmbeddingProvider(dim=64)
    store = InMemoryVectorStore()
    from learning_assistant.models.rag import RetrievedChunk

    chunks = [RetrievedChunk(content="Python basics", score=1.0, chunk_id="1")]
    embs = await emb.embed_documents(["Python basics"])
    await store.add_documents(chunks, embs)
    retriever = SimilarityRetriever(emb, store)
    pipeline = RetrievalPipeline(retriever)
    ctx = await pipeline.run("Python", top_k=1)
    assert len(ctx.chunks) >= 1
    assert ctx.retrieval_time_ms >= 0
    assert ctx.query == "Python"
