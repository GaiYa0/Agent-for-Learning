"""Abstract MCP server interface."""

from abc import ABC, abstractmethod

from learning_assistant.mcp.client.base import MCPPrompt, MCPResource, MCPToolDef, MCPToolResult


class BaseMCPServer(ABC):
    """Provider-agnostic MCP server interface."""

    @abstractmethod
    async def start(self) -> None:
        ...

    @abstractmethod
    async def stop(self) -> None:
        ...

    @abstractmethod
    async def list_tools(self) -> list[MCPToolDef]:
        ...

    @abstractmethod
    async def call_tool(self, name: str, arguments: dict[str, str]) -> MCPToolResult:
        ...

    @abstractmethod
    async def list_resources(self) -> list[MCPResource]:
        ...

    @abstractmethod
    async def get_resource(self, uri: str) -> MCPResource:
        ...

    @abstractmethod
    async def list_prompts(self) -> list[MCPPrompt]:
        ...
