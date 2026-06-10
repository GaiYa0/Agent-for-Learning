"""Tests for EmbeddingFactory."""

import pytest

from learning_assistant.rag.embeddings.factory import EmbeddingFactory
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider


class TestEmbeddingFactory:
    def test_create_mock_default(self) -> None:
        provider = EmbeddingFactory.create("mock")
        assert isinstance(provider, MockEmbeddingProvider)
        assert provider.dimension == 384

    def test_create_mock_custom_dim(self) -> None:
        provider = EmbeddingFactory.create("mock", dim=64)
        assert provider.dimension == 64

    def test_create_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown embedding provider"):
            EmbeddingFactory.create("nonexistent")

    def test_available_contains_mock(self) -> None:
        available = EmbeddingFactory.available()
        assert "mock" in available

    def test_register_custom(self) -> None:
        class CustomProvider(MockEmbeddingProvider):
            pass

        EmbeddingFactory.register("custom", CustomProvider)
        provider = EmbeddingFactory.create("custom")
        assert isinstance(provider, CustomProvider)

    def test_available_after_register(self) -> None:
        available = EmbeddingFactory.available()
        assert len(available) >= 1
