"""Abstract MCP client interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class MCPToolDef:
    name: str
    description: str
    input_schema: dict[str, object] = field(default_factory=dict)


@dataclass
class MCPResource:
    uri: str
    name: str
    content: str = ""
    mime_type: str = "text/plain"


@dataclass
class MCPPrompt:
    name: str
    description: str
    arguments: list[dict[str, str]] = field(default_factory=list)


@dataclass
class MCPToolResult:
    content: str
    is_error: bool = False


class BaseMCPClient(ABC):
    """Provider-agnostic MCP client interface."""

    @abstractmethod
    async def connect(self) -> None:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
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
