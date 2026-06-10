"""Abstract search provider interface."""

from abc import ABC, abstractmethod

from learning_assistant.models.search import SearchResponse


class SearchProvider(ABC):
    """Base class for web search providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @abstractmethod
    async def search(
        self, query: str, max_results: int = 5
    ) -> SearchResponse:
        ...
