"""Tests for VectorStoreFactory."""

import pytest

from learning_assistant.rag.vectorstores.factory import VectorStoreFactory
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


class TestVectorStoreFactory:
    def test_create_memory(self) -> None:
        store = VectorStoreFactory.create("memory")
        assert isinstance(store, InMemoryVectorStore)

    def test_create_default(self) -> None:
        store = VectorStoreFactory.create()
        assert isinstance(store, InMemoryVectorStore)

    def test_create_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown vector store"):
            VectorStoreFactory.create("nonexistent")
