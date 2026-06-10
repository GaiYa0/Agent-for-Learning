"""Tests for DuckDuckGoSearchProvider."""

from unittest.mock import MagicMock

import pytest

from learning_assistant.services.exceptions import ProviderError
from learning_assistant.services.search.duckduckgo_provider import (
    DuckDuckGoSearchProvider,
)


def _make_mock_ddg(results: list[dict[str, str]]) -> MagicMock:
    ddg = MagicMock()
    ddg.text.return_value = results
    return ddg


@pytest.fixture()
def provider() -> DuckDuckGoSearchProvider:
    return DuckDuckGoSearchProvider(ddg_factory=lambda: _make_mock_ddg([]))


class TestDuckDuckGoProvider:
    def test_provider_name(self, provider: DuckDuckGoSearchProvider) -> None:
        assert provider.provider_name == "duckduckgo"

    @pytest.mark.asyncio
    async def test_search_returns_response(
        self, provider: DuckDuckGoSearchProvider
    ) -> None:
        mock_ddg = _make_mock_ddg(
            [
                {"title": "R1", "href": "https://a.com", "body": "snippet1"},
                {"title": "R2", "href": "https://b.com", "body": "snippet2"},
            ]
        )
        provider._ddg_factory = lambda: mock_ddg
        resp = await provider.search("test query", max_results=2)
        assert resp.query == "test query"
        assert resp.provider == "duckduckgo"
        assert resp.result_count() == 2
        assert resp.results[0].title == "R1"

    @pytest.mark.asyncio
    async def test_search_empty_query_raises(
        self, provider: DuckDuckGoSearchProvider
    ) -> None:
        with pytest.raises(ProviderError, match="must not be empty"):
            await provider.search("")

    @pytest.mark.asyncio
    async def test_search_whitespace_query_raises(
        self, provider: DuckDuckGoSearchProvider
    ) -> None:
        with pytest.raises(ProviderError, match="must not be empty"):
            await provider.search("   ")

    @pytest.mark.asyncio
    async def test_search_network_error_raises(
        self, provider: DuckDuckGoSearchProvider
    ) -> None:
        def failing_factory() -> MagicMock:
            ddg = MagicMock()
            ddg.text.side_effect = ConnectionError("network down")
            return ddg

        provider._ddg_factory = failing_factory
        with pytest.raises(ProviderError, match="failed"):
            await provider.search("query")

    @pytest.mark.asyncio
    async def test_search_empty_results(
        self, provider: DuckDuckGoSearchProvider
    ) -> None:
        mock_ddg = _make_mock_ddg([])
        provider._ddg_factory = lambda: mock_ddg
        resp = await provider.search("no results")
        assert resp.result_count() == 0

    @pytest.mark.asyncio
    async def test_search_skips_invalid_results(
        self, provider: DuckDuckGoSearchProvider
    ) -> None:
        mock_ddg = _make_mock_ddg(
            [
                {"title": "", "href": "https://a.com", "body": "skip"},
                {"title": "Valid", "href": "https://b.com", "body": "ok"},
            ]
        )
        provider._ddg_factory = lambda: mock_ddg
        resp = await provider.search("query")
        assert resp.result_count() == 1
        assert resp.results[0].title == "Valid"
