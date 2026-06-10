"""Tests for MCPToolProvider."""

import pytest

from learning_assistant.mcp.client.base import MCPToolDef, MCPToolResult
from learning_assistant.mcp.discovery.capability_manager import CapabilityManager
from learning_assistant.mcp.tool_provider import MCPToolProvider
from tests.mcp.mock_mcp_server import MockMCPServer


@pytest.fixture()
def server() -> MockMCPServer:
    s = MockMCPServer()
    s.add_tool(
        MCPToolDef(name="remote_calc", description="Remote calculator"),
        MCPToolResult(content="42"),
    )
    s.add_tool(
        MCPToolDef(name="remote_search", description="Remote search"),
        MCPToolResult(content="results"),
    )
    return s


@pytest.fixture()
def provider(server: MockMCPServer) -> MCPToolProvider:
    return MCPToolProvider(client=server, capabilities=CapabilityManager())


class TestMCPToolProvider:
    @pytest.mark.asyncio
    async def test_discover_tools(self, provider: MCPToolProvider) -> None:
        tools = await provider.discover_tools()
        assert len(tools) == 2
        assert provider.has_tool("remote_calc")

    @pytest.mark.asyncio
    async def test_call_tool(self, provider: MCPToolProvider) -> None:
        await provider.discover_tools()
        result = await provider.call_tool("remote_calc", {"input": "6*7"})
        assert result.is_success()
        assert result.content == "42"

    @pytest.mark.asyncio
    async def test_call_unknown_tool(self, provider: MCPToolProvider) -> None:
        await provider.discover_tools()
        result = await provider.call_tool("nonexistent", {})
        assert result.is_failure()

    @pytest.mark.asyncio
    async def test_get_tool_definitions(self, provider: MCPToolProvider) -> None:
        await provider.discover_tools()
        defs = provider.get_tool_definitions()
        assert len(defs) == 2
        names = {d["name"] for d in defs}
        assert "remote_calc" in names

    @pytest.mark.asyncio
    async def test_register_to_tool_registry(self, provider: MCPToolProvider) -> None:
        from learning_assistant.tools.registry import ToolRegistry

        await provider.discover_tools()
        registry = ToolRegistry()
        names = provider.register_to(registry)
        assert len(names) == 2
        assert registry.exists(names[0])

    def test_has_tool_false(self, provider: MCPToolProvider) -> None:
        assert provider.has_tool("nonexistent") is False
