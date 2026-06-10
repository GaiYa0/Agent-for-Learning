"""Vector store factory."""

from learning_assistant.rag.vectorstores.base import VectorStore
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


class VectorStoreFactory:
    """Creates vector store instances from configuration."""

    @classmethod
    def create(
        cls, name: str = "memory", collection_name: str = "default"
    ) -> VectorStore:
        if name == "memory":
            return InMemoryVectorStore()
        if name == "chroma":
            from learning_assistant.rag.vectorstores.chroma_store import ChromaVectorStore

            return ChromaVectorStore(collection_name=collection_name)
        available = ["memory", "chroma"]
        raise ValueError(f"Unknown vector store: '{name}'. Available: {available}")
