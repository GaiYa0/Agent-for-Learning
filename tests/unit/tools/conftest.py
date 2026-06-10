"""Shared fixtures for tool tests."""

from learning_assistant.models.tool import ToolResult
from learning_assistant.tools.base import BaseTool, ParameterSpec


class StubTool(BaseTool):
    """Minimal tool for testing registry/manager logic."""

    def __init__(
        self,
        tool_name: str = "stub",
        tool_description: str = "A stub tool",
        tool_category: str = "test",
        result_content: str = "ok",
        should_fail: bool = False,
    ) -> None:
        self._name = tool_name
        self._description = tool_description
        self._category = tool_category
        self._result_content = result_content
        self._should_fail = should_fail

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def category(self) -> str:
        return self._category

    @property
    def parameters(self) -> dict[str, ParameterSpec]:
        return {
            "input": ParameterSpec(
                type="string", description="Some input", required=True
            ),
        }

    async def execute(self, **kwargs: str) -> ToolResult:
        if self._should_fail:
            raise RuntimeError("tool failed")
        return ToolResult(
            tool_call_id="", success=True, content=self._result_content
        )
