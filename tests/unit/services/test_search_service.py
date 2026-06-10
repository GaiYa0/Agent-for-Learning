"""Tests for SearchService provider fallback."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from learning_assistant.services.exceptions import ProviderError
from learning_assistant.services.search.duckduckgo_provider import (
    DuckDuckGoSearchProvider,
)
from learning_assistant.services.search.search_service import SearchService
from learning_assistant.services.search.tavily_provider import TavilySearchProvider


@pytest.mark.asyncio
async def test_tavily_failure_falls_back_to_duckduckgo() -> None:
    service = SearchService(default_provider="tavily")
    failing_tavily = MagicMock(spec=TavilySearchProvider)
    failing_tavily.provider_name = "tavily"
    failing_tavily.search = AsyncMock(
        side_effect=ProviderError("Tavily search failed: timeout")
    )

    ddg = MagicMock(spec=DuckDuckGoSearchProvider)
    ddg.provider_name = "duckduckgo"
    from learning_assistant.models.search import SearchResponse

    ddg.search = AsyncMock(
        return_value=SearchResponse(
            query="q", results=[], provider="duckduckgo", duration_ms=1
        )
    )

    service.register_provider(failing_tavily)
    service.register_provider(ddg)

    resp = await service.search("q")
    assert resp.provider == "duckduckgo"
    ddg.search.assert_awaited_once()
