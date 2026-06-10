"""Tavily search provider implementation."""

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError
from tavily import TavilyClient

from learning_assistant.models.search import SearchResponse, SearchResult
from learning_assistant.services.exceptions import ProviderError
from learning_assistant.services.search.search_provider import SearchProvider

logger = logging.getLogger(__name__)

TavilyClientFactory = Callable[[str], TavilyClient]


class TavilySearchProvider(SearchProvider):
    """Searches the web via Tavily API."""

    def __init__(
        self,
        api_key: str,
        client_factory: TavilyClientFactory | None = None,
    ) -> None:
        self._api_key = api_key
        self._client_factory = client_factory or (lambda key: TavilyClient(api_key=key))

    @property
    def provider_name(self) -> str:
        return "tavily"

    async def search(
        self, query: str, max_results: int = 5
    ) -> SearchResponse:
        if not query.strip():
            raise ProviderError("Search query must not be empty")
        start = time.monotonic()
        try:
            client = self._client_factory(self._api_key)
            raw = await asyncio.to_thread(
                client.search, query, max_results=max_results
            )
        except Exception as e:
            raise ProviderError(f"Tavily search failed: {e}") from e
        elapsed_ms = int((time.monotonic() - start) * 1000)
        results = self._sanitize_results(raw.get("results", []))
        return SearchResponse(
            query=query,
            results=results,
            provider=self.provider_name,
            duration_ms=elapsed_ms,
        )

    @staticmethod
    def _sanitize_results(raw: list[dict[str, Any]]) -> list[SearchResult]:
        results: list[SearchResult] = []
        for item in raw:
            title = (item.get("title") or "").strip()
            url = (item.get("url") or "").strip()
            if not title or not url:
                continue
            snippet = item.get("content") or item.get("snippet") or ""
            score = float(item.get("score", 0.0) or 0.0)
            try:
                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        snippet=str(snippet),
                        score=min(max(score, 0.0), 1.0),
                    )
                )
            except ValidationError:
                continue
        return results
