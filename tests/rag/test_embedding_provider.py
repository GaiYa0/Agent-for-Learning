"""Tests for embedding providers — offline only."""

import pytest

from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider


class TestEmbeddingProviderInterface:
    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            EmbeddingProvider()  # type: ignore[abstract]


class TestMockEmbeddingProvider:
    @pytest.fixture()
    def provider(self) -> MockEmbeddingProvider:
        return MockEmbeddingProvider(dim=384)

    def test_dimension(self, provider: MockEmbeddingProvider) -> None:
        assert provider.dimension == 384

    @pytest.mark.asyncio
    async def test_embed_query_length(self, provider: MockEmbeddingProvider) -> None:
        emb = await provider.embed_query("hello")
        assert len(emb) == 384

    @pytest.mark.asyncio
    async def test_embed_query_deterministic(
        self, provider: MockEmbeddingProvider
    ) -> None:
        emb1 = await provider.embed_query("test")
        emb2 = await provider.embed_query("test")
        assert emb1 == emb2

    @pytest.mark.asyncio
    async def test_embed_query_different_inputs(
        self, provider: MockEmbeddingProvider
    ) -> None:
        emb1 = await provider.embed_query("hello")
        emb2 = await provider.embed_query("world")
        assert emb1 != emb2

    @pytest.mark.asyncio
    async def test_embed_documents(self, provider: MockEmbeddingProvider) -> None:
        embs = await provider.embed_documents(["a", "b", "c"])
        assert len(embs) == 3
        assert all(len(e) == 384 for e in embs)

    @pytest.mark.asyncio
    async def test_embed_documents_deterministic(
        self, provider: MockEmbeddingProvider
    ) -> None:
        embs1 = await provider.embed_documents(["x", "y"])
        embs2 = await provider.embed_documents(["x", "y"])
        assert embs1 == embs2

    @pytest.mark.asyncio
    async def test_normalized(self, provider: MockEmbeddingProvider) -> None:
        emb = await provider.embed_query("normalize test")
        norm = sum(v * v for v in emb) ** 0.5
        assert abs(norm - 1.0) < 1e-6
