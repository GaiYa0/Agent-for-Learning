"""Abstract retriever interface."""

from abc import ABC, abstractmethod

from learning_assistant.models.rag import RetrievedChunk


class Retriever(ABC):
    """Provider-agnostic retriever interface."""

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        ...
