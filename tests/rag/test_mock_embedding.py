"""Additional mock embedding edge cases."""

import pytest

from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider


class TestMockEmbeddingEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_string(self) -> None:
        p = MockEmbeddingProvider(dim=10)
        emb = await p.embed_query("")
        assert len(emb) == 10

    @pytest.mark.asyncio
    async def test_long_text(self) -> None:
        p = MockEmbeddingProvider(dim=64)
        long_text = "word " * 10000
        emb = await p.embed_query(long_text)
        assert len(emb) == 64

    @pytest.mark.asyncio
    async def test_unicode(self) -> None:
        p = MockEmbeddingProvider(dim=32)
        emb = await p.embed_query("你好世界 🌍")
        assert len(emb) == 32

    @pytest.mark.asyncio
    async def test_custom_dimension(self) -> None:
        p = MockEmbeddingProvider(dim=64)
        assert p.dimension == 64
        emb = await p.embed_query("test")
        assert len(emb) == 64
