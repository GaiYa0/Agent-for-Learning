"""Tests for build_llm factory."""

import pytest

from learning_assistant.agent.llm.factory import build_llm
from learning_assistant.agent.llm.mock import MockLLM
from learning_assistant.agent.llm.openai_provider import OpenAICompatibleLLM
from learning_assistant.config.settings import AppSettings


class TestBuildLLM:
    def test_openai_provider_returns_compatible_client(
        self, settings: AppSettings
    ) -> None:
        llm = build_llm(settings)
        assert isinstance(llm, OpenAICompatibleLLM)

    def test_anthropic_provider_returns_mock(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        settings = AppSettings()  # type: ignore[call-arg]
        llm = build_llm(settings)
        assert isinstance(llm, MockLLM)
