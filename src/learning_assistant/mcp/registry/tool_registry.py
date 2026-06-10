"""MCP tool registry — manages MCP tools from multiple servers."""

from learning_assistant.mcp.client.base import MCPToolDef


class MCPToolRegistry:
    """Registry for MCP-discovered tools."""

    def __init__(self) -> None:
        self._tools: dict[str, MCPToolDef] = {}
        self._server_map: dict[str, str] = {}

    def register(self, tool: MCPToolDef, server_id: str = "") -> None:
        self._tools[tool.name] = tool
        if server_id:
            self._server_map[tool.name] = server_id

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)
        self._server_map.pop(name, None)

    def get(self, name: str) -> MCPToolDef | None:
        return self._tools.get(name)

    def list_tools(self) -> list[MCPToolDef]:
        return list(self._tools.values())

    def count(self) -> int:
        return len(self._tools)

    def get_server_id(self, name: str) -> str:
        return self._server_map.get(name, "")

    def remove_by_server(self, server_id: str) -> None:
        names = [
            name for name, sid in self._server_map.items() if sid == server_id
        ]
        for name in names:
            self.unregister(name)
