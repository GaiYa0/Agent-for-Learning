"""Mock MCP server for offline testing."""

from learning_assistant.mcp.client.base import MCPPrompt, MCPResource, MCPToolDef, MCPToolResult
from learning_assistant.mcp.server.base import BaseMCPServer


class MockMCPServer(BaseMCPServer):
    """Configurable mock MCP server."""

    def __init__(self) -> None:
        self._tools: list[MCPToolDef] = []
        self._resources: list[MCPResource] = []
        self._prompts: list[MCPPrompt] = []
        self._tool_results: dict[str, MCPToolResult] = {}
        self.call_log: list[tuple[str, dict[str, str]]] = []

    def add_tool(self, tool: MCPToolDef, result: MCPToolResult | None = None) -> None:
        self._tools.append(tool)
        if result:
            self._tool_results[tool.name] = result

    def add_resource(self, resource: MCPResource) -> None:
        self._resources.append(resource)

    def add_prompt(self, prompt: MCPPrompt) -> None:
        self._prompts.append(prompt)

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def list_tools(self) -> list[MCPToolDef]:
        return self._tools

    async def call_tool(self, name: str, arguments: dict[str, str]) -> MCPToolResult:
        self.call_log.append((name, arguments))
        result = self._tool_results.get(name)
        if result:
            return result
        return MCPToolResult(content=f"No result configured for: {name}", is_error=True)

    async def list_resources(self) -> list[MCPResource]:
        return self._resources

    async def get_resource(self, uri: str) -> MCPResource:
        for r in self._resources:
            if r.uri == uri:
                return r
        return MCPResource(uri=uri, name="not_found", content="")

    async def list_prompts(self) -> list[MCPPrompt]:
        return self._prompts
