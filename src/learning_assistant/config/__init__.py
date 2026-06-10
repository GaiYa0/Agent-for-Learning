"""Configuration layer — typed settings, structured logging, and system constants."""

from learning_assistant.config.constants import (
    DEFAULT_LLM_PROVIDER,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MODEL,
    DEFAULT_SEARCH_PROVIDER,
    DEFAULT_TEMPERATURE,
    SUPPORTED_LLM_PROVIDERS,
    SUPPORTED_SEARCH_PROVIDERS,
    Environment,
    LLMProvider,
    SearchProvider,
)
from learning_assistant.config.logging import setup_logging
from learning_assistant.config.settings import AppSettings, get_settings

__all__ = [
    "AppSettings",
    "DEFAULT_LLM_PROVIDER",
    "DEFAULT_MAX_ITERATIONS",
    "DEFAULT_MODEL",
    "DEFAULT_SEARCH_PROVIDER",
    "DEFAULT_TEMPERATURE",
    "Environment",
    "LLMProvider",
    "SearchProvider",
    "SUPPORTED_LLM_PROVIDERS",
    "SUPPORTED_SEARCH_PROVIDERS",
    "get_settings",
    "setup_logging",
]
