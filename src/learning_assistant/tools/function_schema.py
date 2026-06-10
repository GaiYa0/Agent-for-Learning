"""Converts tools into function-calling schemas for LLM providers."""

from typing import TypedDict

from learning_assistant.tools.base import BaseTool


class OpenAIFunction(TypedDict):
    type: str
    function: dict[str, object]


class MCPToolSchema(TypedDict):
    name: str
    description: str
    inputSchema: dict[str, object]


class ToolSchemaConverter:
    """Produces provider-specific schemas from a BaseTool."""

    @staticmethod
    def to_openai(tool: BaseTool) -> OpenAIFunction:
        raw = tool.schema()
        return OpenAIFunction(
            type="function",
            function={
                "name": str(raw["name"]),
                "description": str(raw["description"]),
                "parameters": raw["parameters"],
            },
        )

    @staticmethod
    def to_json_schema(tool: BaseTool) -> dict[str, object]:
        return tool.schema()

    @staticmethod
    def to_mcp(tool: BaseTool) -> MCPToolSchema:
        raw = tool.schema()
        return MCPToolSchema(
            name=str(raw["name"]),
            description=str(raw["description"]),
            inputSchema=raw["parameters"],  # type: ignore[typeddict-item]
        )
