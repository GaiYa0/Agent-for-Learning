"""Tool orchestrator — coordinates tool execution."""

from learning_assistant.models.tool import ToolResult
from learning_assistant.tools.manager import ToolManager
from learning_assistant.tools.registry import ToolRegistry


class ToolOrchestrator:
    """Coordinates tool calls."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry
        self._manager = ToolManager(registry)

    async def execute(self, tool_name: str, **kwargs: str) -> ToolResult:
        return await self._manager.execute_by_name(tool_name, **kwargs)

    async def execute_chain(
        self, calls: list[tuple[str, dict[str, str]]]
    ) -> list[ToolResult]:
        results: list[ToolResult] = []
        for tool_name, args in calls:
            result = await self._manager.execute_by_name(tool_name, **args)
            results.append(result)
        return results

    def get_available_tools(self) -> list[str]:
        return [t.name for t in self._registry.list_tools()]
