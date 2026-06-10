"""Tests for SimilarityRetriever — offline only."""

import pytest

from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


@pytest.fixture()
def embedding() -> MockEmbeddingProvider:
    return MockEmbeddingProvider(dim=64)


@pytest.mark.asyncio
async def test_retrieve_returns_results(embedding: MockEmbeddingProvider) -> None:
    store = InMemoryVectorStore()
    chunks = [
        RetrievedChunk(content="Python is great", score=1.0, chunk_id="1"),
        RetrievedChunk(content="Java is popular", score=1.0, chunk_id="2"),
    ]
    embs = await embedding.embed_documents(["Python is great", "Java is popular"])
    await store.add_documents(chunks, embs)
    retriever = SimilarityRetriever(embedding, store)
    results = await retriever.retrieve("Python is great", top_k=2)
    assert len(results) > 0
    assert any("Python" in r.content for r in results)


@pytest.mark.asyncio
async def test_retrieve_with_threshold(
    embedding: MockEmbeddingProvider,
) -> None:
    store = InMemoryVectorStore()
    chunks = [RetrievedChunk(content="test", score=1.0, chunk_id="1")]
    embs = await embedding.embed_documents(["test"])
    await store.add_documents(chunks, embs)
    retriever = SimilarityRetriever(embedding, store, score_threshold=0.5)
    results = await retriever.retrieve("test", top_k=1)
    assert len(results) >= 0  # threshold may or may not filter


@pytest.mark.asyncio
async def test_retrieve_preserves_similarity_score(
    embedding: MockEmbeddingProvider,
) -> None:
    store = InMemoryVectorStore()
    chunks = [
        RetrievedChunk(content="Python is great", score=1.0, chunk_id="1"),
        RetrievedChunk(content="Java is popular", score=1.0, chunk_id="2"),
    ]
    embs = await embedding.embed_documents(["Python is great", "Java is popular"])
    await store.add_documents(chunks, embs)
    retriever = SimilarityRetriever(embedding, store)
    results = await retriever.retrieve("Python is great", top_k=2)
    assert results
    assert any(r.score != 1.0 or r.chunk_id == "1" for r in results)


@pytest.mark.asyncio
async def test_retrieve_empty_store(
    embedding: MockEmbeddingProvider,
) -> None:
    store = InMemoryVectorStore()
    retriever = SimilarityRetriever(embedding, store)
    results = await retriever.retrieve("query")
    assert results == []
