"""DuckDuckGo search provider implementation."""

import asyncio
import time
from collections.abc import Callable

from duckduckgo_search import DDGS
from pydantic import ValidationError

from learning_assistant.models.search import SearchResponse, SearchResult
from learning_assistant.services.exceptions import ProviderError
from learning_assistant.services.search.search_provider import SearchProvider

_DDGFactory = Callable[[], DDGS]


class DuckDuckGoSearchProvider(SearchProvider):
    """Searches the web via DuckDuckGo."""

    def __init__(self, ddg_factory: _DDGFactory | None = None) -> None:
        self._ddg_factory = ddg_factory or DDGS

    @property
    def provider_name(self) -> str:
        return "duckduckgo"

    async def search(
        self, query: str, max_results: int = 5
    ) -> SearchResponse:
        if not query.strip():
            raise ProviderError("Search query must not be empty")
        start = time.monotonic()
        try:
            ddg = self._ddg_factory()
            raw = await asyncio.to_thread(
                lambda: list(ddg.text(query, max_results=max_results))
            )
        except Exception as e:
            raise ProviderError(f"DuckDuckGo search failed: {e}") from e
        elapsed_ms = int((time.monotonic() - start) * 1000)
        results = self._sanitize_results(raw)
        return SearchResponse(
            query=query,
            results=results,
            provider=self.provider_name,
            duration_ms=elapsed_ms,
        )

    @staticmethod
    def _sanitize_results(raw: list[dict[str, str]]) -> list[SearchResult]:
        results: list[SearchResult] = []
        for item in raw:
            title = (item.get("title") or "").strip()
            url = (item.get("href") or "").strip()
            if not title or not url:
                continue
            try:
                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        snippet=item.get("body", ""),
                    )
                )
            except ValidationError:
                continue
        return results
