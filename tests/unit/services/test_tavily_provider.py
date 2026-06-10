"""Tests for TavilySearchProvider."""

from unittest.mock import MagicMock

import pytest

from learning_assistant.services.exceptions import ProviderError
from learning_assistant.services.search.tavily_provider import TavilySearchProvider


def _make_mock_client(results: list[dict[str, object]]) -> MagicMock:
    client = MagicMock()
    client.search.return_value = {"results": results}
    return client


@pytest.fixture()
def provider() -> TavilySearchProvider:
    return TavilySearchProvider(
        api_key="test-key",
        client_factory=lambda _key: _make_mock_client([]),
    )


class TestTavilySearchProvider:
    def test_provider_name(self, provider: TavilySearchProvider) -> None:
        assert provider.provider_name == "tavily"

    @pytest.mark.asyncio
    async def test_search_returns_response(
        self, provider: TavilySearchProvider
    ) -> None:
        mock_client = _make_mock_client(
            [
                {
                    "title": "Result 1",
                    "url": "https://a.com",
                    "content": "snippet1",
                    "score": 0.9,
                },
                {
                    "title": "Result 2",
                    "url": "https://b.com",
                    "content": "snippet2",
                },
            ]
        )
        provider._client_factory = lambda _key: mock_client
        resp = await provider.search("test query", max_results=2)
        assert resp.query == "test query"
        assert resp.provider == "tavily"
        assert resp.result_count() == 2
        assert resp.results[0].title == "Result 1"
        mock_client.search.assert_called_once_with("test query", max_results=2)

    @pytest.mark.asyncio
    async def test_search_empty_query_raises(
        self, provider: TavilySearchProvider
    ) -> None:
        with pytest.raises(ProviderError, match="must not be empty"):
            await provider.search("")

    @pytest.mark.asyncio
    async def test_search_api_error_raises(
        self, provider: TavilySearchProvider
    ) -> None:
        failing = MagicMock()
        failing.search.side_effect = RuntimeError("api down")
        provider._client_factory = lambda _key: failing
        with pytest.raises(ProviderError, match="Tavily search failed"):
            await provider.search("query")

    @pytest.mark.asyncio
    async def test_search_skips_invalid_results(
        self, provider: TavilySearchProvider
    ) -> None:
        mock_client = _make_mock_client(
            [
                {"title": "", "url": "https://a.com", "content": "skip"},
                {"title": "Valid", "url": "https://b.com", "content": "ok"},
            ]
        )
        provider._client_factory = lambda _key: mock_client
        resp = await provider.search("query")
        assert resp.result_count() == 1
        assert resp.results[0].title == "Valid"
