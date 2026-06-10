"""Tests for MCPPromptAdapter."""

from learning_assistant.mcp.adapters.prompt_adapter import MCPPromptAdapter
from learning_assistant.prompts.system_prompt import SystemPrompt


class TestMCPPromptAdapter:
    def test_to_mcp_prompt(self) -> None:
        prompt = SystemPrompt()
        mcp_prompt = MCPPromptAdapter.to_mcp_prompt(prompt)
        assert mcp_prompt.name == "system"
        assert len(mcp_prompt.arguments) > 0
        assert mcp_prompt.arguments[0]["name"] == "custom_instructions"
