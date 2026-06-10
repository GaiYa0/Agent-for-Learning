"""Tests for MCP JSON-RPC protocol helpers."""

import pytest

from learning_assistant.mcp.client.protocol import (
    parse_resource_content,
    parse_tool_content,
    unwrap_result,
)
from learning_assistant.mcp.exceptions import MCPError


class TestUnwrapResult:
    def test_extracts_result_object(self) -> None:
        payload = {"jsonrpc": "2.0", "id": "1", "result": {"tools": []}}
        assert unwrap_result(payload) == {"tools": []}

    def test_passthrough_flat_payload(self) -> None:
        payload = {"tools": [{"name": "t1"}]}
        assert unwrap_result(payload)["tools"][0]["name"] == "t1"

    def test_raises_on_error(self) -> None:
        with pytest.raises(MCPError, match="boom"):
            unwrap_result({"error": {"message": "boom"}})


class TestParseToolContent:
    def test_string_content(self) -> None:
        text, is_error = parse_tool_content({"content": "ok", "isError": False})
        assert text == "ok"
        assert is_error is False

    def test_content_blocks(self) -> None:
        text, is_error = parse_tool_content(
            {
                "content": [
                    {"type": "text", "text": "line1"},
                    {"type": "text", "text": "line2"},
                ],
                "isError": False,
            }
        )
        assert text == "line1\nline2"
        assert is_error is False


class TestParseResourceContent:
    def test_direct_content(self) -> None:
        assert parse_resource_content({"content": "hello"}) == "hello"

    def test_contents_array(self) -> None:
        payload = {"contents": [{"text": "from array"}]}
        assert parse_resource_content(payload) == "from array"
