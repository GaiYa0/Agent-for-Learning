"""Tests for HTTP MCP transport."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from learning_assistant.mcp.client.transport import HTTPTransport, TransportMessage


class TestHTTPTransport:
    @pytest.mark.asyncio
    async def test_send_posts_jsonrpc(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": "1",
            "result": {"tools": []},
        }

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        transport = HTTPTransport("http://localhost:8080/mcp", client=mock_client)
        payload = await transport.send(
            TransportMessage(method="tools/list", params={}, id="1")
        )

        assert payload["result"] == {"tools": []}
        mock_client.post.assert_awaited_once()
        call_kwargs = mock_client.post.call_args.kwargs
        assert call_kwargs["json"]["method"] == "tools/list"
        assert call_kwargs["json"]["jsonrpc"] == "2.0"

    @pytest.mark.asyncio
    async def test_send_raises_on_http_error(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error",
            request=MagicMock(),
            response=MagicMock(status_code=500),
        )

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        transport = HTTPTransport("http://localhost:8080/mcp", client=mock_client)
        with pytest.raises(httpx.HTTPStatusError):
            await transport.send(
                TransportMessage(method="tools/list", params={}, id="1")
            )
