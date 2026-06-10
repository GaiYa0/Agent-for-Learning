"""Mock LLM for offline testing — re-exports production mock."""

from learning_assistant.agent.llm.mock import MockLLM, MockLLMResponse

__all__ = ["MockLLM", "MockLLMResponse"]
