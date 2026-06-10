"""MCP resource server — exposes resources via MCP protocol."""

from learning_assistant.mcp.client.base import MCPPrompt, MCPResource, MCPToolDef, MCPToolResult
from learning_assistant.mcp.server.base import BaseMCPServer


class MCPResourceServer(BaseMCPServer):
    """Exposes documents and data as MCP resources."""

    def __init__(self) -> None:
        self._resources: dict[str, MCPResource] = {}

    def register_resource(self, resource: MCPResource) -> None:
        self._resources[resource.uri] = resource

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        self._resources.clear()

    async def list_tools(self) -> list[MCPToolDef]:
        return []

    async def call_tool(self, name: str, arguments: dict[str, str]) -> MCPToolResult:
        return MCPToolResult(content="not a tool server", is_error=True)

    async def list_resources(self) -> list[MCPResource]:
        return list(self._resources.values())

    async def get_resource(self, uri: str) -> MCPResource:
        resource = self._resources.get(uri)
        if resource is None:
            return MCPResource(uri=uri, name="not_found", content="")
        return resource

    async def list_prompts(self) -> list[MCPPrompt]:
        return []
