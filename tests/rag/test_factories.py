"""Tests for RAG factories."""

import pytest

from learning_assistant.rag.embeddings.factory import EmbeddingFactory
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.retrievers.factory import RetrieverFactory
from learning_assistant.rag.retrievers.hybrid import HybridRetriever
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.factory import VectorStoreFactory
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


class TestEmbeddingFactory:
    def test_create_mock(self) -> None:
        provider = EmbeddingFactory.create("mock", dim=64)
        assert isinstance(provider, MockEmbeddingProvider)
        assert provider.dimension == 64

    def test_create_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown"):
            EmbeddingFactory.create("nonexistent")

    def test_available(self) -> None:
        assert "mock" in EmbeddingFactory.available()


class TestVectorStoreFactory:
    def test_create_memory(self) -> None:
        store = VectorStoreFactory.create("memory")
        assert isinstance(store, InMemoryVectorStore)

    def test_create_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown"):
            VectorStoreFactory.create("nonexistent")


class TestRetrieverFactory:
    def test_create_similarity(self) -> None:
        emb = MockEmbeddingProvider(dim=64)
        store = InMemoryVectorStore()
        retriever = RetrieverFactory.create_similarity(emb, store)
        assert isinstance(retriever, SimilarityRetriever)

    def test_create_similarity_with_threshold(self) -> None:
        emb = MockEmbeddingProvider(dim=64)
        store = InMemoryVectorStore()
        retriever = RetrieverFactory.create_similarity(emb, store, score_threshold=0.5)
        assert retriever._threshold == 0.5

    def test_create_hybrid(self) -> None:
        emb = MockEmbeddingProvider(dim=64)
        store = InMemoryVectorStore()
        primary = SimilarityRetriever(emb, store)
        hybrid = RetrieverFactory.create_hybrid(primary)
        assert isinstance(hybrid, HybridRetriever)
