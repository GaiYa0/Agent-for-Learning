"""Tests for vector store exceptions."""

from learning_assistant.rag.exceptions import RAGError
from learning_assistant.rag.vectorstores.exceptions import VectorStoreError


class TestVectorStoreExceptions:
    def test_inherits_rag_error(self) -> None:
        assert issubclass(VectorStoreError, RAGError)

    def test_message(self) -> None:
        e = VectorStoreError("test error")
        assert str(e).endswith("test error")
