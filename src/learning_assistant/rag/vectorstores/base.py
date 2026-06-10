"""Abstract vector store interface."""

from abc import ABC, abstractmethod

from learning_assistant.models.rag import RetrievedChunk


class VectorStore(ABC):
    """Provider-agnostic vector store interface."""

    @abstractmethod
    async def add_documents(
        self,
        chunks: list[RetrievedChunk],
        embeddings: list[list[float]],
    ) -> None:
        ...

    @abstractmethod
    async def delete_documents(self, chunk_ids: list[str]) -> None:
        ...

    @abstractmethod
    async def similarity_search(
        self, embedding: list[float], top_k: int = 5
    ) -> list[RetrievedChunk]:
        ...

    @abstractmethod
    async def similarity_search_with_score(
        self, embedding: list[float], top_k: int = 5
    ) -> list[tuple[RetrievedChunk, float]]:
        ...

    @abstractmethod
    async def count(self) -> int:
        ...

    @abstractmethod
    async def clear(self) -> None:
        ...
