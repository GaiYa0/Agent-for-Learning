"""Tests for InMemoryVectorStore — offline only."""

import pytest

from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


@pytest.fixture()
def store() -> InMemoryVectorStore:
    return InMemoryVectorStore()


@pytest.fixture()
def sample_chunks() -> list[RetrievedChunk]:
    return [
        RetrievedChunk(content="chunk A", score=1.0, chunk_id="a", source="doc.pdf"),
        RetrievedChunk(content="chunk B", score=1.0, chunk_id="b", source="doc.pdf"),
        RetrievedChunk(content="chunk C", score=1.0, chunk_id="c", source="doc.pdf"),
    ]


class TestInMemoryVectorStore:
    @pytest.mark.asyncio
    async def test_empty(self, store: InMemoryVectorStore) -> None:
        assert await store.count() == 0

    @pytest.mark.asyncio
    async def test_add_and_count(
        self, store: InMemoryVectorStore, sample_chunks: list[RetrievedChunk]
    ) -> None:
        embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        await store.add_documents(sample_chunks, embeddings)
        assert await store.count() == 3

    @pytest.mark.asyncio
    async def test_similarity_search(
        self, store: InMemoryVectorStore, sample_chunks: list[RetrievedChunk]
    ) -> None:
        embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        await store.add_documents(sample_chunks, embeddings)
        results = await store.similarity_search([1.0, 0.0, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0].content == "chunk A"

    @pytest.mark.asyncio
    async def test_similarity_with_score(
        self, store: InMemoryVectorStore, sample_chunks: list[RetrievedChunk]
    ) -> None:
        embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        await store.add_documents(sample_chunks, embeddings)
        results = await store.similarity_search_with_score([1.0, 0.0, 0.0], top_k=1)
        assert len(results) == 1
        chunk, score = results[0]
        assert chunk.content == "chunk A"
        assert score > 0.99

    @pytest.mark.asyncio
    async def test_delete(
        self, store: InMemoryVectorStore, sample_chunks: list[RetrievedChunk]
    ) -> None:
        embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        await store.add_documents(sample_chunks, embeddings)
        await store.delete_documents(["a"])
        assert await store.count() == 2

    @pytest.mark.asyncio
    async def test_clear(
        self, store: InMemoryVectorStore, sample_chunks: list[RetrievedChunk]
    ) -> None:
        embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        await store.add_documents(sample_chunks, embeddings)
        await store.clear()
        assert await store.count() == 0

    @pytest.mark.asyncio
    async def test_empty_search(self, store: InMemoryVectorStore) -> None:
        results = await store.similarity_search([1.0, 0.0], top_k=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_zero_vector_search(
        self, store: InMemoryVectorStore, sample_chunks: list[RetrievedChunk]
    ) -> None:
        await store.add_documents(sample_chunks, [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        results = await store.similarity_search([0.0, 0.0], top_k=5)
        assert results == []
