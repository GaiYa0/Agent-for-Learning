"""Mock search provider for offline testing."""

from learning_assistant.models.search import SearchResponse, SearchResult
from learning_assistant.services.search.search_provider import SearchProvider


class MockSearchProvider(SearchProvider):
    """Returns pre-configured search results."""

    def __init__(
        self,
        results: list[SearchResult] | None = None,
        should_fail: bool = False,
    ) -> None:
        self._results = results or []
        self._should_fail = should_fail
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return "mock"

    async def search(self, query: str, max_results: int = 5) -> SearchResponse:
        self.call_count += 1
        if self._should_fail:
            raise ConnectionError("Mock search failure")
        return SearchResponse(
            query=query,
            results=self._results[:max_results],
            provider=self.provider_name,
        )

    @classmethod
    def with_results(cls, titles: list[str]) -> "MockSearchProvider":
        results = [
            SearchResult(title=t, url=f"https://example.com/{t}", snippet=f"About {t}")
            for t in titles
        ]
        return cls(results=results)

    @classmethod
    def empty(cls) -> "MockSearchProvider":
        return cls(results=[])

    @classmethod
    def failing(cls) -> "MockSearchProvider":
        return cls(should_fail=True)
