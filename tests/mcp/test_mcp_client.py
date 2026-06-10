"""Tests for MCP client and session."""

import pytest

from learning_assistant.mcp.client.mcp_client import MCPClient
from learning_assistant.mcp.client.session import MCPSession
from learning_assistant.mcp.exceptions import MCPError
from learning_assistant.mcp.client.transport import MCPTransport, TransportMessage


class MockTransport(MCPTransport):
    def __init__(self) -> None:
        self.call_log: list[TransportMessage] = []
        self._responses: dict[str, dict] = {}

    def set_response(self, method: str, response: dict) -> None:
        self._responses[method] = response

    async def send(self, message: TransportMessage) -> dict:
        self.call_log.append(message)
        return self._responses.get(message.method, {"result": {}})

    async def close(self) -> None:
        pass


@pytest.fixture()
def transport() -> MockTransport:
    t = MockTransport()
    t.set_response(
        "tools/list",
        {
            "result": {
                "tools": [
                    {
                        "name": "test_tool",
                        "description": "A test tool",
                        "inputSchema": {},
                    }
                ]
            }
        },
    )
    t.set_response(
        "tools/call",
        {
            "result": {
                "content": [{"type": "text", "text": "result"}],
                "isError": False,
            }
        },
    )
    t.set_response(
        "resources/list",
        {"result": {"resources": [{"uri": "file:///test", "name": "test.txt"}]}},
    )
    t.set_response(
        "resources/read",
        {"result": {"name": "test.txt", "content": "hello"}},
    )
    t.set_response(
        "prompts/list",
        {
            "result": {
                "prompts": [{"name": "test_prompt", "description": "A test prompt"}]
            }
        },
    )
    return t


class TestMCPSession:
    def test_init(self) -> None:
        session = MCPSession()
        assert session.is_connected is False

    @pytest.mark.asyncio
    async def test_connect(self) -> None:
        session = MCPSession()
        await session.connect()
        assert session.is_connected is True

    @pytest.mark.asyncio
    async def test_disconnect(self) -> None:
        session = MCPSession()
        await session.connect()
        await session.disconnect()
        assert session.is_connected is False


class TestMCPClient:
    @pytest.mark.asyncio
    async def test_connect(self, transport: MockTransport) -> None:
        client = MCPClient(transport)
        await client.connect()
        assert client.session.is_connected is True

    @pytest.mark.asyncio
    async def test_disconnect(self, transport: MockTransport) -> None:
        client = MCPClient(transport)
        await client.connect()
        await client.disconnect()
        assert client.session.is_connected is False

    @pytest.mark.asyncio
    async def test_list_tools(self, transport: MockTransport) -> None:
        client = MCPClient(transport)
        await client.connect()
        tools = await client.list_tools()
        assert len(tools) == 1
        assert tools[0].name == "test_tool"

    @pytest.mark.asyncio
    async def test_call_tool(self, transport: MockTransport) -> None:
        client = MCPClient(transport)
        await client.connect()
        result = await client.call_tool("test_tool", {"input": "x"})
        assert result.content == "result"
        assert result.is_error is False

    @pytest.mark.asyncio
    async def test_list_resources(self, transport: MockTransport) -> None:
        client = MCPClient(transport)
        await client.connect()
        resources = await client.list_resources()
        assert len(resources) == 1
        assert resources[0].uri == "file:///test"

    @pytest.mark.asyncio
    async def test_get_resource(self, transport: MockTransport) -> None:
        client = MCPClient(transport)
        await client.connect()
        resource = await client.get_resource("file:///test")
        assert resource.content == "hello"

    @pytest.mark.asyncio
    async def test_list_prompts(self, transport: MockTransport) -> None:
        client = MCPClient(transport)
        await client.connect()
        prompts = await client.list_prompts()
        assert len(prompts) == 1
        assert prompts[0].name == "test_prompt"

    @pytest.mark.asyncio
    async def test_jsonrpc_error_raises(self, transport: MockTransport) -> None:
        transport.set_response(
            "tools/call",
            {"error": {"code": -32601, "message": "Method not found"}},
        )
        client = MCPClient(transport)
        await client.connect()
        with pytest.raises(MCPError, match="Method not found"):
            await client.call_tool("missing", {})
