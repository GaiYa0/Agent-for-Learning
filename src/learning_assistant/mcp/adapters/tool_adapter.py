"""Tool adapter — bridges local tools to MCP tool definitions."""

from learning_assistant.mcp.client.base import MCPToolDef, MCPToolResult
from learning_assistant.tools.base import BaseTool


class MCPToolAdapter:
    """Adapts local BaseTool instances to MCP protocol format."""

    @staticmethod
    def to_mcp_tool(tool: BaseTool) -> MCPToolDef:
        schema = tool.schema()
        params = schema.get("parameters", {})
        return MCPToolDef(
            name=tool.name,
            description=tool.description,
            input_schema=params if isinstance(params, dict) else {},
        )

    @staticmethod
    def from_mcp_result(result: MCPToolResult) -> str:
        return result.content

    @staticmethod
    def to_mcp_result(content: str, is_error: bool = False) -> MCPToolResult:
        return MCPToolResult(content=content, is_error=is_error)
