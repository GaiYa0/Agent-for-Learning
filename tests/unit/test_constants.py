"""Tests for system constants."""

from learning_assistant.config.constants import (
    DEFAULT_LLM_PROVIDER,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MODEL,
    DEFAULT_SEARCH_PROVIDER,
    DEFAULT_TEMPERATURE,
    SUPPORTED_LLM_PROVIDERS,
    SUPPORTED_SEARCH_PROVIDERS,
)


class TestConstants:
    def test_default_model_is_string(self) -> None:
        assert isinstance(DEFAULT_MODEL, str)
        assert len(DEFAULT_MODEL) > 0

    def test_default_max_iterations_is_positive(self) -> None:
        assert isinstance(DEFAULT_MAX_ITERATIONS, int)
        assert DEFAULT_MAX_ITERATIONS >= 1

    def test_default_temperature_in_valid_range(self) -> None:
        assert isinstance(DEFAULT_TEMPERATURE, float)
        assert 0.0 <= DEFAULT_TEMPERATURE <= 2.0

    def test_supported_llm_providers_is_non_empty_tuple(self) -> None:
        assert isinstance(SUPPORTED_LLM_PROVIDERS, tuple)
        assert len(SUPPORTED_LLM_PROVIDERS) > 0
        assert all(isinstance(p, str) for p in SUPPORTED_LLM_PROVIDERS)

    def test_supported_search_providers_is_non_empty_tuple(self) -> None:
        assert isinstance(SUPPORTED_SEARCH_PROVIDERS, tuple)
        assert len(SUPPORTED_SEARCH_PROVIDERS) > 0

    def test_openai_in_supported_providers(self) -> None:
        assert "openai" in SUPPORTED_LLM_PROVIDERS

    def test_tavily_in_supported_providers(self) -> None:
        assert "tavily" in SUPPORTED_SEARCH_PROVIDERS

    def test_default_llm_provider_in_supported(self) -> None:
        assert DEFAULT_LLM_PROVIDER in SUPPORTED_LLM_PROVIDERS

    def test_default_search_provider_in_supported(self) -> None:
        assert DEFAULT_SEARCH_PROVIDER in SUPPORTED_SEARCH_PROVIDERS
