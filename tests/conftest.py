"""Shared fixtures for all test modules."""

from collections.abc import Generator

import pytest

from learning_assistant.config.settings import AppSettings, get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Generator[None, None, None]:
    """Ensure each test starts with a fresh settings singleton."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def valid_env_vars(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set minimum required env vars for AppSettings to construct."""
    env: dict[str, str] = {
        "OPENAI_API_KEY": "sk-test-key-12345",
        "TAVILY_API_KEY": "tvly-test-key-12345",
        "OPENAI_MODEL": "mimo-v2.5-pro",
        "OPENAI_BASE_URL": "https://token-plan-cn.xiaomimimo.com/v1",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return env


@pytest.fixture()
def full_env_vars(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set all env vars including optional ones."""
    env: dict[str, str] = {
        "OPENAI_API_KEY": "sk-test-key-12345",
        "OPENAI_MODEL": "gpt-4o",
        "TAVILY_API_KEY": "tvly-test-key-12345",
        "LLM_PROVIDER": "openai",
        "SEARCH_PROVIDER": "tavily",
        "AGENT_MAX_ITERATIONS": "10",
        "AGENT_TEMPERATURE": "0.5",
        "LOG_LEVEL": "DEBUG",
        "ENVIRONMENT": "testing",
        "APP_NAME": "test-agent",
        "APP_VERSION": "1.0.0",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return env


@pytest.fixture()
def settings(valid_env_vars: dict[str, str]) -> AppSettings:
    """Pre-built AppSettings with minimal valid config."""
    return AppSettings()  # type: ignore[call-arg]
