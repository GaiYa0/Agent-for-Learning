"""Abstract base class for all tools."""

from abc import ABC, abstractmethod
from typing import TypedDict

from learning_assistant.models.tool import ToolResult


class ParameterSpec(TypedDict):
    type: str
    description: str
    required: bool


class BaseTool(ABC):
    """Common interface every tool must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @property
    @abstractmethod
    def category(self) -> str:
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict[str, ParameterSpec]:
        ...

    @abstractmethod
    async def execute(self, **kwargs: str) -> ToolResult:
        ...

    @property
    def primary_parameter(self) -> str:
        """Name of the main input parameter for single-string tool invocation."""
        for key, spec in self.parameters.items():
            if spec["required"]:
                return key
        return "input"

    def validate(self, **kwargs: str) -> None:
        """Override to add custom validation before execute()."""
        required = {k for k, v in self.parameters.items() if v["required"]}
        missing = required - set(kwargs.keys())
        if missing:
            from learning_assistant.tools.exceptions import ToolValidationError

            raise ToolValidationError(f"Missing required parameters: {missing}")

    def schema(self) -> dict[str, object]:
        """Return a JSON-serialisable schema describing this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parameters": {
                "type": "object",
                "properties": {
                    k: {"type": v["type"], "description": v["description"]}
                    for k, v in self.parameters.items()
                },
                "required": [
                    k for k, v in self.parameters.items() if v["required"]
                ],
            },
        }
