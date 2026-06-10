"""Prompt adapter — bridges local prompts to MCP prompt format."""

from learning_assistant.mcp.client.base import MCPPrompt
from learning_assistant.prompts.base import BasePromptTemplate


class MCPPromptAdapter:
    """Adapts local BasePromptTemplate to MCP protocol format."""

    @staticmethod
    def to_mcp_prompt(prompt: BasePromptTemplate) -> MCPPrompt:
        return MCPPrompt(
            name=prompt.name,
            description=f"Prompt template v{prompt.version}",
            arguments=[
                {"name": var, "required": "true"}
                for var in prompt.required_variables
            ],
        )
