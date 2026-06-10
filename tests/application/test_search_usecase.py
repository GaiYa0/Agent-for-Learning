"""Tests for SearchUseCase."""

import pytest

from learning_assistant.application.dto.search_request import SearchRequest
from learning_assistant.application.orchestrators.tool_orchestrator import ToolOrchestrator
from learning_assistant.application.usecases.search_usecase import SearchUseCase
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_tool import MockTool


@pytest.fixture()
def usecase() -> SearchUseCase:
    registry = ToolRegistry()
    registry.register(MockTool(tool_name="web_search", result_content="Search results"))
    orch = ToolOrchestrator(registry)
    return SearchUseCase(orch)


class TestSearchUseCase:
    @pytest.mark.asyncio
    async def test_success(self, usecase: SearchUseCase) -> None:
        req = SearchRequest(query="Python")
        result = await usecase.execute(req)
        assert result.success is True
        assert result.data is not None
        assert result.data.query == "Python"

    @pytest.mark.asyncio
    async def test_empty_query(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SearchRequest(query="")
