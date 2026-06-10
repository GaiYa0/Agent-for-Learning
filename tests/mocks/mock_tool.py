"""Mock tool for offline testing."""

from learning_assistant.models.tool import ToolResult
from learning_assistant.tools.base import BaseTool, ParameterSpec


class MockTool(BaseTool):
    """Configurable mock tool for testing."""

    def __init__(
        self,
        tool_name: str = "mock_tool",
        tool_description: str = "A mock tool",
        tool_category: str = "test",
        result_content: str = "mock result",
        should_fail: bool = False,
        error_message: str = "mock error",
    ) -> None:
        self._name = tool_name
        self._description = tool_description
        self._category = tool_category
        self._result_content = result_content
        self._should_fail = should_fail
        self._error_message = error_message
        self.call_count = 0
        self.last_kwargs: dict[str, str] = {}

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
                type="string", description="Input text", required=True
            ),
        }

    async def execute(self, **kwargs: str) -> ToolResult:
        self.call_count += 1
        self.last_kwargs = dict(kwargs)
        if self._should_fail:
            return ToolResult(
                tool_call_id="",
                success=False,
                content="",
                error=self._error_message,
            )
        return ToolResult(
            tool_call_id="",
            success=True,
            content=self._result_content,
        )

    @classmethod
    def failing(cls, name: str = "failing_tool", error: str = "tool failed") -> "MockTool":
        return cls(tool_name=name, should_fail=True, error_message=error)
