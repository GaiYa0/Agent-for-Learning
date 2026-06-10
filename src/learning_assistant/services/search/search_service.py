"""Search service — manages multiple providers and delegates queries."""

import logging

from learning_assistant.models.search import SearchResponse
from learning_assistant.services.base import BaseService
from learning_assistant.services.exceptions import ProviderError, SearchError
from learning_assistant.services.search.search_provider import SearchProvider

logger = logging.getLogger(__name__)


class SearchService(BaseService):
    """Routes search queries to registered providers."""

    def __init__(self, default_provider: str | None = None) -> None:
        self._providers: dict[str, SearchProvider] = {}
        self._default_provider_name: str | None = default_provider

    @property
    def service_name(self) -> str:
        return "search"

    async def health_check(self) -> bool:
        return len(self._providers) > 0

    async def close(self) -> None:
        self._providers.clear()

    def register_provider(self, provider: SearchProvider) -> None:
        self._providers[provider.provider_name] = provider
        if self._default_provider_name is None:
            self._default_provider_name = provider.provider_name

    def set_default_provider(self, name: str) -> None:
        if name not in self._providers:
            raise SearchError(f"Provider not registered: {name}")
        self._default_provider_name = name

    def remove_provider(self, name: str) -> None:
        self._providers.pop(name, None)
        if self._default_provider_name == name:
            remaining = list(self._providers.keys())
            self._default_provider_name = remaining[0] if remaining else None

    def get_provider(self, name: str | None = None) -> SearchProvider:
        target = name or self._default_provider_name
        if target is None:
            raise SearchError("No search provider registered")
        provider = self._providers.get(target)
        if provider is None:
            raise ProviderError(f"Provider not found: {target}")
        return provider

    async def search(
        self,
        query: str,
        max_results: int = 5,
        provider_name: str | None = None,
    ) -> SearchResponse:
        provider = self.get_provider(provider_name)
        try:
            return await provider.search(query, max_results=max_results)
        except ProviderError as exc:
            if (
                provider.provider_name == "tavily"
                and "duckduckgo" in self._providers
            ):
                logger.warning(
                    "Tavily search failed (%s); falling back to duckduckgo",
                    exc,
                )
                fallback = self._providers["duckduckgo"]
                return await fallback.search(query, max_results=max_results)
            raise
