"""Registry-based tool factory."""

from collections.abc import Callable

from learning_assistant.tools.base import BaseTool
from learning_assistant.tools.exceptions import ToolRegistrationError

ToolCreator = Callable[[], BaseTool]


class ToolFactory:
    """Creates tools from a creator registry."""

    def __init__(self) -> None:
        self._creators: dict[str, ToolCreator] = {}

    def register(self, name: str, creator: ToolCreator) -> None:
        if name in self._creators:
            raise ToolRegistrationError(f"Creator already registered: '{name}'")
        self._creators[name] = creator

    def create(self, name: str) -> BaseTool:
        creator = self._creators.get(name)
        if creator is None:
            available = ", ".join(sorted(self._creators.keys()))
            raise ToolRegistrationError(
                f"Unknown tool: '{name}'. Available: [{available}]"
            )
        return creator()

    def available_tools(self) -> list[str]:
        return sorted(self._creators.keys())
