"""MCP resource registry — manages MCP resources."""

from learning_assistant.mcp.client.base import MCPResource


class MCPResourceRegistry:
    """Registry for MCP-discovered resources."""

    def __init__(self) -> None:
        self._resources: dict[str, MCPResource] = {}

    def register(self, resource: MCPResource) -> None:
        self._resources[resource.uri] = resource

    def unregister(self, uri: str) -> None:
        self._resources.pop(uri, None)

    def get(self, uri: str) -> MCPResource | None:
        return self._resources.get(uri)

    def list_resources(self) -> list[MCPResource]:
        return list(self._resources.values())

    def count(self) -> int:
        return len(self._resources)
