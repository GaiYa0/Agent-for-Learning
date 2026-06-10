"""MCP tool provider — bridges MCP tools into the local tool system."""

from typing import Any

from learning_assistant.mcp.adapters.mcp_tool_wrapper import MCPToolWrapper
from learning_assistant.mcp.client.base import BaseMCPClient, MCPToolDef
from learning_assistant.mcp.discovery.capability_manager import CapabilityManager
from learning_assistant.models.tool import ToolResult
from learning_assistant.tools.registry import ToolRegistry


class MCPToolProvider:
    """Wraps MCP tools as local BaseTool instances for unified agent access."""

    def __init__(
        self,
        client: BaseMCPClient,
        capabilities: CapabilityManager | None = None,
        server_id: str = "default",
    ) -> None:
        self._client = client
        self._capabilities = capabilities or CapabilityManager()
        self._server_id = server_id

    async def discover_tools(self, server_id: str | None = None) -> list[MCPToolDef]:
        sid = server_id or self._server_id
        tools = await self._client.list_tools()
        self._capabilities.register_tools(tools, server_id=sid)
        return tools

    async def call_tool(self, name: str, arguments: dict[str, str]) -> ToolResult:
        try:
            result = await self._client.call_tool(name, arguments)
            return ToolResult(
                tool_call_id="",
                success=not result.is_error,
                content=result.content,
                error=result.content if result.is_error else None,
            )
        except Exception as e:
            return ToolResult(
                tool_call_id="",
                success=False,
                content="",
                error=str(e),
            )

    def register_to(
        self,
        registry: ToolRegistry,
        *,
        prefix: str = "mcp",
        server_id: str | None = None,
    ) -> list[str]:
        """Register discovered MCP tools into the local ToolRegistry."""
        sid = server_id or self._server_id
        registered: list[str] = []
        for tool in self._capabilities.tool_registry.list_tools():
            reg_name = f"{prefix}_{sid}_{tool.name}".replace("-", "_")
            wrapper = MCPToolWrapper(tool, self._client, reg_name)
            registry.register(wrapper, allow_override=True)
            registered.append(reg_name)
        return registered

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        tools = self._capabilities.tool_registry.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.input_schema,
            }
            for t in tools
        ]

    def has_tool(self, name: str) -> bool:
        return self._capabilities.tool_registry.get(name) is not None
