"""Tests for ToolSchemaConverter."""

from learning_assistant.tools.function_schema import ToolSchemaConverter
from tests.unit.tools.conftest import StubTool


class TestToolSchemaConverter:
    def test_to_openai(self) -> None:
        tool = StubTool(tool_name="test", tool_description="desc")
        result = ToolSchemaConverter.to_openai(tool)
        assert result["type"] == "function"
        assert result["function"]["name"] == "test"
        assert result["function"]["description"] == "desc"
        assert "parameters" in result["function"]

    def test_to_json_schema(self) -> None:
        tool = StubTool()
        result = ToolSchemaConverter.to_json_schema(tool)
        assert "name" in result
        assert "parameters" in result

    def test_to_mcp(self) -> None:
        tool = StubTool(tool_name="mcp_tool")
        result = ToolSchemaConverter.to_mcp(tool)
        assert result["name"] == "mcp_tool"
        assert "inputSchema" in result

    def test_openai_schema_has_required_fields(self) -> None:
        tool = StubTool()
        result = ToolSchemaConverter.to_openai(tool)
        params = result["function"]["parameters"]
        assert "input" in params["required"]

    def test_mcp_schema_structure(self) -> None:
        tool = StubTool()
        result = ToolSchemaConverter.to_mcp(tool)
        schema = result["inputSchema"]
        assert schema["type"] == "object"
        assert "input" in schema["properties"]
