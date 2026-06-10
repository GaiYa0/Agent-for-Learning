"""Tests for ServerDiscovery."""

import pytest

from learning_assistant.mcp.client.transport import HTTPTransport, SSETransport, StdioTransport
from learning_assistant.mcp.discovery.server_discovery import ServerConfig, ServerDiscovery
from learning_assistant.mcp.exceptions import MCPDiscoveryError


@pytest.fixture()
def discovery() -> ServerDiscovery:
    return ServerDiscovery()


class TestServerDiscovery:
    def test_register_server(self, discovery: ServerDiscovery) -> None:
        config = ServerConfig(server_id="s1", transport_type="stdio")
        discovery.register_server(config)
        assert len(discovery.list_servers()) == 1

    def test_unregister_server(self, discovery: ServerDiscovery) -> None:
        discovery.register_server(ServerConfig(server_id="s1", transport_type="stdio"))
        discovery.unregister_server("s1")
        assert len(discovery.list_servers()) == 0

    def test_create_stdio_transport(self, discovery: ServerDiscovery) -> None:
        discovery.register_server(ServerConfig(server_id="s1", transport_type="stdio"))
        transport = discovery.create_transport("s1")
        assert isinstance(transport, StdioTransport)

    def test_create_http_transport(self, discovery: ServerDiscovery) -> None:
        discovery.register_server(
            ServerConfig(server_id="s1", transport_type="http", url="http://localhost:8080")
        )
        transport = discovery.create_transport("s1")
        assert isinstance(transport, HTTPTransport)

    def test_create_sse_transport(self, discovery: ServerDiscovery) -> None:
        discovery.register_server(
            ServerConfig(server_id="s1", transport_type="sse", url="http://localhost:8080")
        )
        transport = discovery.create_transport("s1")
        assert isinstance(transport, SSETransport)

    def test_unknown_server_raises(self, discovery: ServerDiscovery) -> None:
        with pytest.raises(MCPDiscoveryError, match="not found"):
            discovery.create_transport("nonexistent")

    def test_unknown_transport_raises(self, discovery: ServerDiscovery) -> None:
        discovery.register_server(ServerConfig(server_id="s1", transport_type="unknown"))
        with pytest.raises(MCPDiscoveryError, match="Unknown transport"):
            discovery.create_transport("s1")
