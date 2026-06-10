"""Capability manager — manages MCP capabilities across servers."""

from learning_assistant.mcp.client.base import MCPPrompt, MCPResource, MCPToolDef
from learning_assistant.mcp.registry.prompt_registry import MCPPromptRegistry
from learning_assistant.mcp.registry.resource_registry import MCPResourceRegistry
from learning_assistant.mcp.registry.tool_registry import MCPToolRegistry


class CapabilityManager:
    """Manages tools, resources, and prompts from multiple MCP servers."""

    def __init__(self) -> None:
        self._tools = MCPToolRegistry()
        self._resources = MCPResourceRegistry()
        self._prompts = MCPPromptRegistry()

    @property
    def tool_registry(self) -> MCPToolRegistry:
        return self._tools

    @property
    def resource_registry(self) -> MCPResourceRegistry:
        return self._resources

    @property
    def prompt_registry(self) -> MCPPromptRegistry:
        return self._prompts

    def register_tools(self, tools: list[MCPToolDef], server_id: str = "") -> None:
        for tool in tools:
            self._tools.register(tool, server_id)

    def register_resources(self, resources: list[MCPResource]) -> None:
        for resource in resources:
            self._resources.register(resource)

    def register_prompts(self, prompts: list[MCPPrompt]) -> None:
        for prompt in prompts:
            self._prompts.register(prompt)

    def remove_server(self, server_id: str) -> None:
        self._tools.remove_by_server(server_id)

    def tool_count(self) -> int:
        return self._tools.count()

    def resource_count(self) -> int:
        return self._resources.count()

    def prompt_count(self) -> int:
        return self._prompts.count()
