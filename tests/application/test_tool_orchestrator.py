"""Tests for ToolOrchestrator."""

import pytest

from learning_assistant.application.orchestrators.tool_orchestrator import ToolOrchestrator
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_tool import MockTool


@pytest.fixture()
def orchestrator() -> ToolOrchestrator:
    registry = ToolRegistry()
    registry.register(MockTool(tool_name="t1", result_content="r1"))
    registry.register(MockTool(tool_name="t2", result_content="r2"))
    return ToolOrchestrator(registry)


class TestToolOrchestrator:
    @pytest.mark.asyncio
    async def test_execute(self, orchestrator: ToolOrchestrator) -> None:
        result = await orchestrator.execute("t1", input="x")
        assert result.is_success()
        assert result.content == "r1"

    @pytest.mark.asyncio
    async def test_execute_chain(self, orchestrator: ToolOrchestrator) -> None:
        results = await orchestrator.execute_chain([
            ("t1", {"input": "a"}),
            ("t2", {"input": "b"}),
        ])
        assert len(results) == 2
        assert results[0].content == "r1"
        assert results[1].content == "r2"

    def test_get_available_tools(self, orchestrator: ToolOrchestrator) -> None:
        tools = orchestrator.get_available_tools()
        assert "t1" in tools
        assert "t2" in tools
