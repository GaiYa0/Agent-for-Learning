"""Tests for AppSettings and get_settings."""

import pytest
from pydantic import SecretStr, ValidationError

from learning_assistant.config.settings import AppSettings, get_settings


class TestAppSettingsConstruction:
    def test_creates_with_valid_env(self, settings: AppSettings) -> None:
        assert settings.app_name == "learning-assistant-agent"
        assert settings.app_version == "0.1.0"

    def test_secret_fields_are_secret_str(self, settings: AppSettings) -> None:
        assert isinstance(settings.openai_api_key, SecretStr)
        assert isinstance(settings.tavily_api_key, SecretStr)

    def test_secret_value_not_in_repr(self, settings: AppSettings) -> None:
        repr_str = repr(settings)
        assert "sk-test-key-12345" not in repr_str

    def test_get_secret_extracts_value(self, settings: AppSettings) -> None:
        assert settings.get_secret("openai_api_key") == "sk-test-key-12345"
        assert settings.get_secret("tavily_api_key") == "tvly-test-key-12345"

    def test_get_secret_unknown_field_raises(self, settings: AppSettings) -> None:
        with pytest.raises(ValueError, match="Unknown secret field"):
            settings.get_secret("app_name")

    def test_get_secret_unset_field_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SEARCH_PROVIDER", "duckduckgo")
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        s = AppSettings()  # type: ignore[call-arg]
        with pytest.raises(ValueError, match="not set"):
            s.get_secret("tavily_api_key")

    def test_get_api_keys_parses_csv(self, valid_env_vars: dict[str, str]) -> None:
        s = AppSettings()  # type: ignore[call-arg]
        s.api_keys = " key1 , key2, "
        assert s.get_api_keys() == {"key1", "key2"}

    def test_get_cors_origins_parses_csv(
        self, valid_env_vars: dict[str, str]
    ) -> None:
        s = AppSettings()  # type: ignore[call-arg]
        s.cors_allowed_origins = "http://localhost:8501, http://127.0.0.1:8501"
        assert s.get_cors_origins() == [
            "http://localhost:8501",
            "http://127.0.0.1:8501",
        ]


class TestAppSettingsDefaults:
    def test_default_model(self, settings: AppSettings) -> None:
        assert settings.openai_model == "mimo-v2.5-pro"

    def test_default_openai_base_url(self, settings: AppSettings) -> None:
        assert settings.openai_base_url == "https://token-plan-cn.xiaomimimo.com/v1"

    def test_default_max_iterations(self, settings: AppSettings) -> None:
        assert settings.agent_max_iterations == 5

    def test_default_temperature(self, settings: AppSettings) -> None:
        assert settings.agent_temperature == pytest.approx(0.2)

    def test_default_log_level(self, settings: AppSettings) -> None:
        assert settings.log_level == "INFO"

    def test_default_environment(self, settings: AppSettings) -> None:
        assert settings.environment == "development"

    def test_default_llm_provider(self, settings: AppSettings) -> None:
        assert settings.llm_provider == "openai"

    def test_default_search_provider(self, settings: AppSettings) -> None:
        assert settings.search_provider == "tavily"


class TestAppSettingsOverrides:
    def test_custom_model(self, full_env_vars: dict[str, str]) -> None:
        s = AppSettings()  # type: ignore[call-arg]
        assert s.openai_model == "gpt-4o"

    def test_custom_max_iterations(self, full_env_vars: dict[str, str]) -> None:
        s = AppSettings()  # type: ignore[call-arg]
        assert s.agent_max_iterations == 10

    def test_custom_temperature(self, full_env_vars: dict[str, str]) -> None:
        s = AppSettings()  # type: ignore[call-arg]
        assert s.agent_temperature == pytest.approx(0.5)

    def test_custom_log_level(self, full_env_vars: dict[str, str]) -> None:
        s = AppSettings()  # type: ignore[call-arg]
        assert s.log_level == "DEBUG"


class TestAppSettingsValidation:
    def test_missing_openai_key_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TAVILY_API_KEY", "test")
        monkeypatch.setenv("OPENAI_API_KEY", "")
        with pytest.raises(ValidationError) as exc_info:
            AppSettings()  # type: ignore[call-arg]
        assert "openai_api_key" in str(exc_info.value).lower()

    def test_missing_tavily_key_allowed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test")
        monkeypatch.setenv("SEARCH_PROVIDER", "tavily")
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        s = AppSettings()  # type: ignore[call-arg]
        assert s.search_provider == "tavily"
        assert s.tavily_api_key is None

    def test_invalid_log_level_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LOG_LEVEL", "INVALID")
        with pytest.raises(ValidationError) as exc_info:
            AppSettings()  # type: ignore[call-arg]
        assert "log_level" in str(exc_info.value).lower()

    def test_temperature_too_high_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AGENT_TEMPERATURE", "3.0")
        with pytest.raises(ValidationError):
            AppSettings()  # type: ignore[call-arg]

    def test_temperature_negative_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AGENT_TEMPERATURE", "-0.1")
        with pytest.raises(ValidationError):
            AppSettings()  # type: ignore[call-arg]

    def test_max_iterations_zero_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AGENT_MAX_ITERATIONS", "0")
        with pytest.raises(ValidationError):
            AppSettings()  # type: ignore[call-arg]

    def test_max_iterations_negative_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AGENT_MAX_ITERATIONS", "-1")
        with pytest.raises(ValidationError):
            AppSettings()  # type: ignore[call-arg]

    def test_empty_openai_key_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "   ")
        with pytest.raises(ValidationError) as exc_info:
            AppSettings()  # type: ignore[call-arg]
        assert "openai_api_key" in str(exc_info.value).lower()

    def test_empty_optional_secrets_treated_as_unset(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")
        monkeypatch.setenv("TAVILY_API_KEY", "")
        s = AppSettings()  # type: ignore[call-arg]
        assert s.anthropic_api_key is None
        assert s.tavily_api_key is None

    def test_duckduckgo_without_tavily_key_ok(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SEARCH_PROVIDER", "duckduckgo")
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        s = AppSettings()  # type: ignore[call-arg]
        assert s.search_provider == "duckduckgo"
        assert s.tavily_api_key is None

    def test_anthropic_provider_requires_anthropic_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("SEARCH_PROVIDER", "duckduckgo")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValidationError) as exc_info:
            AppSettings()  # type: ignore[call-arg]
        assert "anthropic_api_key" in str(exc_info.value).lower()

    def test_anthropic_provider_with_key_ok(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.setenv("SEARCH_PROVIDER", "duckduckgo")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        s = AppSettings()  # type: ignore[call-arg]
        assert s.llm_provider == "anthropic"
        assert s.get_secret("anthropic_api_key") == "sk-ant-test-key"

    def test_invalid_environment_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ENVIRONMENT", "invalid-env")
        with pytest.raises(ValidationError):
            AppSettings()  # type: ignore[call-arg]

    def test_invalid_openai_model_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_MODEL", "bad model!")
        with pytest.raises(ValidationError) as exc_info:
            AppSettings()  # type: ignore[call-arg]
        assert "openai_model" in str(exc_info.value).lower()

    def test_empty_openai_model_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_MODEL", "   ")
        with pytest.raises(ValidationError) as exc_info:
            AppSettings()  # type: ignore[call-arg]
        assert "openai_model" in str(exc_info.value).lower()

    def test_invalid_openai_base_url_raises(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_BASE_URL", "not-a-url")
        with pytest.raises(ValidationError) as exc_info:
            AppSettings()  # type: ignore[call-arg]
        assert "openai_base_url" in str(exc_info.value).lower()

    def test_openai_base_url_strips_trailing_slash(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(
            "OPENAI_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1/"
        )
        s = AppSettings()  # type: ignore[call-arg]
        assert s.openai_base_url == "https://token-plan-cn.xiaomimimo.com/v1"


class TestGetSettings:
    def test_returns_app_settings(self, settings: AppSettings) -> None:
        s = get_settings()
        assert isinstance(s, AppSettings)

    def test_returns_same_instance(self, settings: AppSettings) -> None:
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_cache_clear_forces_reload(
        self, valid_env_vars: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        s1 = get_settings()
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        get_settings.cache_clear()
        s2 = get_settings()
        assert s2.openai_model == "gpt-4o"
        assert s1 is not s2
