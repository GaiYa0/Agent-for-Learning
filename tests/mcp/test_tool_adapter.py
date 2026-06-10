"""Tests for MCPToolAdapter."""

from learning_assistant.mcp.adapters.tool_adapter import MCPToolAdapter
from learning_assistant.mcp.client.base import MCPToolResult
from tests.mocks.mock_tool import MockTool


class TestMCPToolAdapter:
    def test_to_mcp_tool(self) -> None:
        tool = MockTool(tool_name="test", tool_description="desc")
        mcp_tool = MCPToolAdapter.to_mcp_tool(tool)
        assert mcp_tool.name == "test"
        assert mcp_tool.description == "desc"
        assert "input" in mcp_tool.input_schema.get("properties", {})

    def test_from_mcp_result(self) -> None:
        result = MCPToolResult(content="hello", is_error=False)
        assert MCPToolAdapter.from_mcp_result(result) == "hello"

    def test_to_mcp_result_success(self) -> None:
        result = MCPToolAdapter.to_mcp_result("ok")
        assert result.content == "ok"
        assert result.is_error is False

    def test_to_mcp_result_error(self) -> None:
        result = MCPToolAdapter.to_mcp_result("err", is_error=True)
        assert result.is_error is True
