"""MCP prompt server — exposes prompts via MCP protocol."""

from learning_assistant.mcp.client.base import MCPPrompt, MCPResource, MCPToolDef, MCPToolResult
from learning_assistant.mcp.server.base import BaseMCPServer


class MCPPromptServer(BaseMCPServer):
    """Exposes prompts as MCP prompts."""

    def __init__(self) -> None:
        self._prompts: dict[str, MCPPrompt] = {}

    def register_prompt(self, prompt: MCPPrompt) -> None:
        self._prompts[prompt.name] = prompt

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        self._prompts.clear()

    async def list_tools(self) -> list[MCPToolDef]:
        return []

    async def call_tool(self, name: str, arguments: dict[str, str]) -> MCPToolResult:
        return MCPToolResult(content="not a tool server", is_error=True)

    async def list_resources(self) -> list[MCPResource]:
        return []

    async def get_resource(self, uri: str) -> MCPResource:
        return MCPResource(uri=uri, name="not_found", content="")

    async def list_prompts(self) -> list[MCPPrompt]:
        return list(self._prompts.values())
