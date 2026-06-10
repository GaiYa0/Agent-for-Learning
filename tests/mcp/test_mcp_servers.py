"""Tests for MCP server implementations."""

import pytest

from learning_assistant.mcp.client.base import MCPPrompt, MCPResource, MCPToolDef
from learning_assistant.mcp.server.prompt_server import MCPPromptServer
from learning_assistant.mcp.server.resource_server import MCPResourceServer
from learning_assistant.mcp.server.tool_server import MCPToolServer


class TestMCPToolServer:
    @pytest.mark.asyncio
    async def test_list_and_call_tool(self) -> None:
        server = MCPToolServer()
        tool = MCPToolDef(name="echo", description="Echo input")

        async def handler(**kwargs: str) -> str:
            return kwargs.get("input", "")

        server.register_tool(tool, handler)
        tools = await server.list_tools()
        assert len(tools) == 1
        assert tools[0].name == "echo"

        result = await server.call_tool("echo", {"input": "hello"})
        assert result.content == "hello"
        assert result.is_error is False

    @pytest.mark.asyncio
    async def test_call_missing_tool(self) -> None:
        server = MCPToolServer()
        result = await server.call_tool("missing", {})
        assert result.is_error is True
        assert "not found" in result.content.lower()


class TestMCPResourceServer:
    @pytest.mark.asyncio
    async def test_list_and_get_resource(self) -> None:
        server = MCPResourceServer()
        resource = MCPResource(uri="file:///a.txt", name="a.txt", content="data")
        server.register_resource(resource)

        resources = await server.list_resources()
        assert len(resources) == 1

        fetched = await server.get_resource("file:///a.txt")
        assert fetched.content == "data"

    @pytest.mark.asyncio
    async def test_get_missing_resource(self) -> None:
        server = MCPResourceServer()
        fetched = await server.get_resource("file:///missing")
        assert fetched.content == ""


class TestMCPPromptServer:
    @pytest.mark.asyncio
    async def test_list_prompts(self) -> None:
        server = MCPPromptServer()
        server.register_prompt(MCPPrompt(name="p1", description="Prompt one"))
        prompts = await server.list_prompts()
        assert len(prompts) == 1
        assert prompts[0].name == "p1"
