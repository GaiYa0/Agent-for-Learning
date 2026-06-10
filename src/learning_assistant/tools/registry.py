"""Tool registry — thread-safe dynamic tool store."""

import threading

from learning_assistant.tools.base import BaseTool
from learning_assistant.tools.exceptions import ToolNotFoundError, ToolRegistrationError


class ToolRegistry:
    """Manages tool registration and lookup."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._lock = threading.Lock()

    def register(self, tool: BaseTool, *, allow_override: bool = False) -> None:
        with self._lock:
            if tool.name in self._tools and not allow_override:
                raise ToolRegistrationError(
                    f"Tool already registered: '{tool.name}'. "
                    "Use allow_override=True to replace."
                )
            self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        with self._lock:
            self._tools.pop(name, None)

    def get(self, name: str) -> BaseTool:
        with self._lock:
            tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFoundError(f"Tool not found: '{name}'")
        return tool

    def exists(self, name: str) -> bool:
        with self._lock:
            return name in self._tools

    def list_tools(self) -> list[BaseTool]:
        with self._lock:
            return list(self._tools.values())

    def count(self) -> int:
        with self._lock:
            return len(self._tools)
