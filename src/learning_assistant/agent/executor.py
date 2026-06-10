"""Action executor — runs tools and captures observations."""

from learning_assistant.models.tool import ToolResult
from learning_assistant.tools.manager import ToolManager


class ActionExecutor:
    """Executes tool calls and returns observations."""

    def __init__(self, tool_manager: ToolManager) -> None:
        self._tool_manager = tool_manager

    async def execute(self, tool_name: str, tool_input: str) -> ToolResult:
        return await self._tool_manager.execute_by_name(
            tool_name, input=tool_input
        )

    async def execute_or_default(
        self, tool_name: str, tool_input: str
    ) -> tuple[str, bool]:
        try:
            result = await self.execute(tool_name, tool_input)
            if result.is_success():
                return result.content, True
            error = result.error or "unknown error"
            return f"Tool error: {error}", False
        except Exception as e:
            return f"Tool execution failed: {e}", False
