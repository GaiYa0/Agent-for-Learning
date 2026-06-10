"""MCP transport abstraction."""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class TransportMessage:
    method: str
    params: dict[str, object]
    id: str = ""


class MCPTransport(ABC):
    """Abstract transport for MCP communication."""

    @abstractmethod
    async def send(self, message: TransportMessage) -> dict[str, object]:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...


class StdioTransport(MCPTransport):
    """Stdio-based transport for local MCP servers."""

    async def send(self, message: TransportMessage) -> dict[str, object]:
        raise NotImplementedError(
            "StdioTransport is not implemented; use HTTPTransport or a mock in tests"
        )

    async def close(self) -> None:
        pass


class HTTPTransport(MCPTransport):
    """HTTP JSON-RPC transport for remote MCP servers."""

    def __init__(
        self,
        url: str,
        timeout: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._url = url.rstrip("/")
        self._timeout = timeout
        self._client = client
        self._owns_client = client is None

    async def send(self, message: TransportMessage) -> dict[str, object]:
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": message.id or str(uuid.uuid4()),
            "method": message.method,
            "params": message.params,
        }
        if self._client is not None:
            response = await self._client.post(
                self._url, json=payload, timeout=self._timeout
            )
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._url, json=payload, timeout=self._timeout
                )
        response.raise_for_status()
        data: dict[str, object] = response.json()
        return data

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()


class SSETransport(MCPTransport):
    """SSE-based transport for streaming MCP servers."""

    def __init__(self, url: str) -> None:
        self._url = url

    async def send(self, message: TransportMessage) -> dict[str, object]:
        raise NotImplementedError(
            "SSETransport is not implemented; use HTTPTransport"
        )

    async def close(self) -> None:
        pass
