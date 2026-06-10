"""MCP factory — creates MCP components."""

from learning_assistant.mcp.client.mcp_client import MCPClient
from learning_assistant.mcp.client.session import SessionConfig
from learning_assistant.mcp.client.transport import (
    HTTPTransport,
    MCPTransport,
    SSETransport,
    StdioTransport,
)
from learning_assistant.mcp.discovery.capability_manager import CapabilityManager
from learning_assistant.mcp.discovery.server_discovery import ServerDiscovery


class MCPFactory:
    """Creates MCP clients, registries, and providers."""

    @staticmethod
    def create_client(
        transport: MCPTransport,
        session_config: SessionConfig | None = None,
    ) -> MCPClient:
        return MCPClient(transport, session_config)

    @staticmethod
    def create_stdio_client() -> MCPClient:
        return MCPClient(StdioTransport())

    @staticmethod
    def create_http_client(url: str) -> MCPClient:
        return MCPClient(HTTPTransport(url))

    @staticmethod
    def create_sse_client(url: str) -> MCPClient:
        return MCPClient(SSETransport(url))

    @staticmethod
    def create_capability_manager() -> CapabilityManager:
        return CapabilityManager()

    @staticmethod
    def create_server_discovery() -> ServerDiscovery:
        return ServerDiscovery()
