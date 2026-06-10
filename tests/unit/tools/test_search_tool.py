"""Tests for SearchTool."""

from unittest.mock import AsyncMock

import pytest

from learning_assistant.models.search import SearchResponse, SearchResult
from learning_assistant.tools.exceptions import ToolExecutionError, ToolValidationError
from learning_assistant.tools.search_tool import SearchTool


def _mock_search_service(results: list[SearchResult] | None = None):
    svc = AsyncMock()
    svc.search.return_value = SearchResponse(
        query="q", results=results or [], provider="mock"
    )
    return svc


@pytest.fixture()
def tool() -> SearchTool:
    return SearchTool(search_service=_mock_search_service())


class TestSearchTool:
    def test_name(self, tool: SearchTool) -> None:
        assert tool.name == "web_search"

    def test_category(self, tool: SearchTool) -> None:
        assert tool.category == "search"

    def test_schema(self, tool: SearchTool) -> None:
        s = tool.schema()
        assert "query" in s["parameters"]["properties"]

    @pytest.mark.asyncio
    async def test_execute_with_results(self) -> None:
        results = [
            SearchResult(title="T", url="https://x.com", snippet="s"),
        ]
        svc = _mock_search_service(results)
        t = SearchTool(search_service=svc)
        result = await t.execute(query="test")
        assert result.is_success()
        assert "T" in result.content

    @pytest.mark.asyncio
    async def test_execute_no_results(self) -> None:
        svc = _mock_search_service([])
        t = SearchTool(search_service=svc)
        result = await t.execute(query="nothing")
        assert result.is_success()
        assert "No results" in result.content

    @pytest.mark.asyncio
    async def test_execute_service_error(self) -> None:
        svc = AsyncMock()
        svc.search.side_effect = ConnectionError("offline")
        t = SearchTool(search_service=svc)
        with pytest.raises(ToolExecutionError, match="Search failed"):
            await t.execute(query="q")

    @pytest.mark.asyncio
    async def test_default_constructor_uses_factory_provider(self) -> None:
        t = SearchTool()
        provider = t._search_service.get_provider()
        assert provider.provider_name == "duckduckgo"

    @pytest.mark.asyncio
    async def test_invalid_max_results_raises(self) -> None:
        svc = _mock_search_service()
        t = SearchTool(search_service=svc)
        with pytest.raises(ToolValidationError, match="max_results"):
            await t.execute(query="q", max_results="abc")
