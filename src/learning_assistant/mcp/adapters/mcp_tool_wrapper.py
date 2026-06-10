"""Wrap MCP tool definitions as local BaseTool instances."""

from learning_assistant.mcp.client.base import BaseMCPClient, MCPToolDef
from learning_assistant.models.tool import ToolResult
from learning_assistant.tools.base import BaseTool, ParameterSpec
from learning_assistant.tools.exceptions import ToolExecutionError


class MCPToolWrapper(BaseTool):
    """Adapts a remote MCP tool for the local ToolManager / ReAct agent."""

    def __init__(
        self,
        tool_def: MCPToolDef,
        client: BaseMCPClient,
        registered_name: str,
    ) -> None:
        self._tool_def = tool_def
        self._client = client
        self._registered_name = registered_name

    @property
    def name(self) -> str:
        return self._registered_name

    @property
    def description(self) -> str:
        return self._tool_def.description

    @property
    def category(self) -> str:
        return "mcp"

    @property
    def parameters(self) -> dict[str, ParameterSpec]:
        schema = self._tool_def.input_schema
        properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
        required = set(schema.get("required", [])) if isinstance(schema, dict) else set()
        if not properties:
            return {
                "input": ParameterSpec(
                    type="string",
                    description="Tool input",
                    required=True,
                )
            }
        params: dict[str, ParameterSpec] = {}
        for key, spec in properties.items():
            if not isinstance(spec, dict):
                params[key] = ParameterSpec(
                    type="string",
                    description=str(spec),
                    required=key in required,
                )
                continue
            params[key] = ParameterSpec(
                type=str(spec.get("type", "string")),
                description=str(spec.get("description", key)),
                required=key in required,
            )
        return params

    async def execute(self, **kwargs: str) -> ToolResult:
        try:
            mcp_result = await self._client.call_tool(self._tool_def.name, kwargs)
            return ToolResult(
                tool_call_id="",
                success=not mcp_result.is_error,
                content=mcp_result.content,
                error=mcp_result.content if mcp_result.is_error else None,
            )
        except Exception as e:
            raise ToolExecutionError(f"MCP tool '{self._tool_def.name}' failed: {e}") from e
