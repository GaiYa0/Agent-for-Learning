"""MCP tool server — exposes tools via MCP protocol."""

from collections.abc import Callable, Coroutine
from typing import Any

from learning_assistant.mcp.client.base import MCPPrompt, MCPResource, MCPToolDef, MCPToolResult
from learning_assistant.mcp.server.base import BaseMCPServer

ToolHandler = Callable[..., Coroutine[Any, Any, str]]


class MCPToolServer(BaseMCPServer):
    """Exposes local tools as MCP tools."""

    def __init__(self) -> None:
        self._tools: dict[str, MCPToolDef] = {}
        self._handlers: dict[str, ToolHandler] = {}

    def register_tool(self, tool_def: MCPToolDef, handler: ToolHandler) -> None:
        self._tools[tool_def.name] = tool_def
        self._handlers[tool_def.name] = handler

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        self._tools.clear()
        self._handlers.clear()

    async def list_tools(self) -> list[MCPToolDef]:
        return list(self._tools.values())

    async def call_tool(self, name: str, arguments: dict[str, str]) -> MCPToolResult:
        handler = self._handlers.get(name)
        if handler is None:
            return MCPToolResult(content=f"Tool not found: {name}", is_error=True)
        try:
            result = await handler(**arguments)
            return MCPToolResult(content=str(result))
        except Exception as e:
            return MCPToolResult(content=str(e), is_error=True)

    async def list_resources(self) -> list[MCPResource]:
        return []

    async def get_resource(self, uri: str) -> MCPResource:
        return MCPResource(uri=uri, name="not_found", content="")

    async def list_prompts(self) -> list[MCPPrompt]:
        return []
