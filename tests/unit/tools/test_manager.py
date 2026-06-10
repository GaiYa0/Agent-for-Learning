"""Tests for ToolManager."""

import pytest

from learning_assistant.tools.exceptions import ToolNotFoundError, ToolValidationError
from learning_assistant.tools.manager import ToolManager
from learning_assistant.tools.registry import ToolRegistry
from tests.unit.tools.conftest import StubTool


@pytest.fixture()
def registry() -> ToolRegistry:
    return ToolRegistry()


@pytest.fixture()
def manager(registry: ToolRegistry) -> ToolManager:
    return ToolManager(registry)


class TestExecute:
    @pytest.mark.asyncio
    async def test_success(self, manager: ToolManager) -> None:
        tool = StubTool(tool_name="t", result_content="done")
        result = await manager.execute(tool, input="hello")
        assert result.success is True
        assert result.content == "done"

    @pytest.mark.asyncio
    async def test_failure_returns_error_result(
        self, manager: ToolManager
    ) -> None:
        tool = StubTool(tool_name="t", should_fail=True)
        result = await manager.execute(tool, input="hello")
        assert result.is_failure() is True
        assert "tool failed" in result.error

    @pytest.mark.asyncio
    async def test_missing_required_param_raises(
        self, manager: ToolManager
    ) -> None:
        tool = StubTool(tool_name="t")
        with pytest.raises(ToolValidationError, match="Missing required"):
            await manager.execute(tool)


class TestExecuteByName:
    @pytest.mark.asyncio
    async def test_success(
        self, manager: ToolManager, registry: ToolRegistry
    ) -> None:
        registry.register(StubTool(tool_name="t", result_content="ok"))
        result = await manager.execute_by_name("t", input="x")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_not_found(self, manager: ToolManager) -> None:
        with pytest.raises(ToolNotFoundError):
            await manager.execute_by_name("missing", input="x")
