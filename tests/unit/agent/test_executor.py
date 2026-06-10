"""Tests for ActionExecutor."""

import pytest

from learning_assistant.agent.executor import ActionExecutor
from learning_assistant.tools.manager import ToolManager
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_tool import MockTool


@pytest.fixture()
def executor() -> ActionExecutor:
    registry = ToolRegistry()
    registry.register(MockTool(tool_name="t1", result_content="result_1"))
    registry.register(MockTool.failing(name="fail_tool", error="boom"))
    return ActionExecutor(ToolManager(registry))


class TestActionExecutor:
    @pytest.mark.asyncio
    async def test_execute_success(self, executor: ActionExecutor) -> None:
        result = await executor.execute("t1", "hello")
        assert result.is_success()
        assert result.content == "result_1"

    @pytest.mark.asyncio
    async def test_execute_failure(self, executor: ActionExecutor) -> None:
        result = await executor.execute("fail_tool", "x")
        assert result.is_failure()

    @pytest.mark.asyncio
    async def test_execute_or_default_success(
        self, executor: ActionExecutor
    ) -> None:
        obs, success = await executor.execute_or_default("t1", "x")
        assert obs == "result_1"
        assert success is True

    @pytest.mark.asyncio
    async def test_execute_or_default_failure(
        self, executor: ActionExecutor
    ) -> None:
        obs, success = await executor.execute_or_default("fail_tool", "x")
        assert "Tool error" in obs
        assert success is False

    @pytest.mark.asyncio
    async def test_execute_or_default_unknown_tool(
        self, executor: ActionExecutor
    ) -> None:
        obs, success = await executor.execute_or_default("nonexistent", "x")
        assert "Tool execution failed" in obs
        assert success is False
