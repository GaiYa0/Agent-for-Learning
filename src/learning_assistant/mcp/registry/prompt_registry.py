"""MCP prompt registry — manages MCP prompts."""

from learning_assistant.mcp.client.base import MCPPrompt


class MCPPromptRegistry:
    """Registry for MCP-discovered prompts."""

    def __init__(self) -> None:
        self._prompts: dict[str, MCPPrompt] = {}

    def register(self, prompt: MCPPrompt) -> None:
        self._prompts[prompt.name] = prompt

    def unregister(self, name: str) -> None:
        self._prompts.pop(name, None)

    def get(self, name: str) -> MCPPrompt | None:
        return self._prompts.get(name)

    def list_prompts(self) -> list[MCPPrompt]:
        return list(self._prompts.values())

    def count(self) -> int:
        return len(self._prompts)
