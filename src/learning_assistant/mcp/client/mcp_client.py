"""MCP client — implements BaseMCPClient with transport and session management."""

from typing import Any

from learning_assistant.mcp.client.base import (
    BaseMCPClient,
    MCPPrompt,
    MCPResource,
    MCPToolDef,
    MCPToolResult,
)
from learning_assistant.mcp.client.protocol import (
    parse_resource_content,
    parse_tool_content,
    unwrap_result,
)
from learning_assistant.mcp.client.session import MCPSession, SessionConfig
from learning_assistant.mcp.client.transport import MCPTransport, TransportMessage


class MCPClient(BaseMCPClient):
    """Full MCP client implementation."""

    def __init__(
        self,
        transport: MCPTransport,
        session_config: SessionConfig | None = None,
    ) -> None:
        self._transport = transport
        self._session = MCPSession(session_config)
        self._tools: list[MCPToolDef] = []
        self._resources: list[MCPResource] = []
        self._prompts: list[MCPPrompt] = []
        self._request_id = 0

    @property
    def session(self) -> MCPSession:
        return self._session

    async def connect(self) -> None:
        await self._session.connect()

    async def disconnect(self) -> None:
        await self._session.disconnect()
        await self._transport.close()

    async def list_tools(self) -> list[MCPToolDef]:
        payload = await self._send_request("tools/list", {})
        result = unwrap_result(payload)
        tools_data: list[dict[str, Any]] = result.get("tools", [])
        self._tools = [
            MCPToolDef(
                name=t.get("name", ""),
                description=t.get("description", ""),
                input_schema=t.get("inputSchema", {}),
            )
            for t in tools_data
        ]
        return self._tools

    async def call_tool(self, name: str, arguments: dict[str, str]) -> MCPToolResult:
        payload = await self._send_request(
            "tools/call",
            {"name": name, "arguments": arguments},
        )
        result = unwrap_result(payload)
        content, is_error = parse_tool_content(result)
        return MCPToolResult(content=content, is_error=is_error)

    async def list_resources(self) -> list[MCPResource]:
        payload = await self._send_request("resources/list", {})
        result = unwrap_result(payload)
        resources_data: list[dict[str, Any]] = result.get("resources", [])
        self._resources = [
            MCPResource(uri=r.get("uri", ""), name=r.get("name", ""))
            for r in resources_data
        ]
        return self._resources

    async def get_resource(self, uri: str) -> MCPResource:
        payload = await self._send_request("resources/read", {"uri": uri})
        result = unwrap_result(payload)
        return MCPResource(
            uri=uri,
            name=result.get("name", uri),
            content=parse_resource_content(result),
        )

    async def list_prompts(self) -> list[MCPPrompt]:
        payload = await self._send_request("prompts/list", {})
        result = unwrap_result(payload)
        prompts_data: list[dict[str, Any]] = result.get("prompts", [])
        self._prompts = [
            MCPPrompt(
                name=p.get("name", ""),
                description=p.get("description", ""),
                arguments=p.get("arguments", []),
            )
            for p in prompts_data
        ]
        return self._prompts

    async def _send_request(
        self, method: str, params: dict[str, object]
    ) -> dict[str, Any]:
        self._request_id += 1
        message = TransportMessage(
            method=method,
            params=params,
            id=str(self._request_id),
        )
        raw: dict[str, Any] = await self._session.execute_with_retry(
            method.replace("/", "_"),
            lambda: self._transport.send(message),
        )
        return raw
