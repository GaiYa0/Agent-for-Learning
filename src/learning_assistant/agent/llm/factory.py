"""Build LLM instances from application settings."""

from learning_assistant.agent.llm.base import BaseLLM
from learning_assistant.agent.llm.mock import MockLLM
from learning_assistant.agent.llm.openai_provider import OpenAICompatibleLLM
from learning_assistant.config.settings import AppSettings


def build_llm(settings: AppSettings) -> BaseLLM:
    """Create an LLM client from settings."""
    if settings.llm_provider == "openai":
        return OpenAICompatibleLLM(
            api_key=settings.get_secret("openai_api_key"),
            model=settings.openai_model,
            base_url=settings.openai_base_url,
            temperature=settings.agent_temperature,
        )
    if settings.llm_provider == "anthropic":
        return MockLLM.with_fixed_reply(
            "LLM provider 'anthropic' adapter not implemented."
        )
    return MockLLM.with_fixed_reply("No LLM provider configured.")
