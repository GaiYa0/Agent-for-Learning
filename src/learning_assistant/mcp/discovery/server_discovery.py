"""Server discovery — finds MCP servers by transport type."""

from dataclasses import dataclass

from learning_assistant.mcp.client.transport import (
    HTTPTransport,
    MCPTransport,
    SSETransport,
    StdioTransport,
)
from learning_assistant.mcp.exceptions import MCPDiscoveryError


@dataclass
class ServerConfig:
    server_id: str
    transport_type: str
    url: str = ""
    command: str = ""


class ServerDiscovery:
    """Discovers and creates transports for MCP servers."""

    def __init__(self) -> None:
        self._servers: dict[str, ServerConfig] = {}

    def register_server(self, config: ServerConfig) -> None:
        self._servers[config.server_id] = config

    def unregister_server(self, server_id: str) -> None:
        self._servers.pop(server_id, None)

    def list_servers(self) -> list[ServerConfig]:
        return list(self._servers.values())

    def create_transport(self, server_id: str) -> MCPTransport:
        config = self._servers.get(server_id)
        if config is None:
            raise MCPDiscoveryError(f"Server not found: {server_id}")
        if config.transport_type == "stdio":
            return StdioTransport()
        if config.transport_type == "http":
            return HTTPTransport(config.url)
        if config.transport_type == "sse":
            return SSETransport(config.url)
        raise MCPDiscoveryError(f"Unknown transport type: {config.transport_type}")
