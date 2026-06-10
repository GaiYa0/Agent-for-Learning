"""Application settings loaded from environment variables and .env files."""

from functools import lru_cache

import re

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from learning_assistant.config.constants import (
    DEFAULT_LLM_PROVIDER,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MCP_TRANSPORT,
    DEFAULT_MODEL,
    DEFAULT_OPENAI_BASE_URL,
    DEFAULT_SEARCH_PROVIDER,
    DEFAULT_TEMPERATURE,
    Environment,
    LLMProvider,
    MCPTransport,
    SearchProvider,
)

_SECRET_FIELDS = frozenset({"openai_api_key", "tavily_api_key", "anthropic_api_key"})
_OPENAI_MODEL_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")


class AppSettings(BaseSettings):
    """Typed, validated application configuration.

    Values are resolved in priority order:
        1. Environment variables
        2. .env file
        3. Defaults defined here
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────
    app_name: str = "learning-assistant-agent"
    app_version: str = "0.1.0"
    environment: Environment = "development"

    # ── Providers ────────────────────────────────────────────────────────
    llm_provider: LLMProvider = DEFAULT_LLM_PROVIDER
    search_provider: SearchProvider = DEFAULT_SEARCH_PROVIDER

    # ── OpenAI ───────────────────────────────────────────────────────────
    openai_api_key: SecretStr | None = None
    openai_base_url: str = DEFAULT_OPENAI_BASE_URL
    openai_model: str = DEFAULT_MODEL

    # ── Anthropic ────────────────────────────────────────────────────────
    anthropic_api_key: SecretStr | None = None

    # ── Search ───────────────────────────────────────────────────────────
    tavily_api_key: SecretStr | None = None

    # ── Agent ────────────────────────────────────────────────────────────
    agent_max_iterations: int = DEFAULT_MAX_ITERATIONS
    agent_temperature: float = DEFAULT_TEMPERATURE

    # ── Logging ──────────────────────────────────────────────────────────
    log_level: str = "INFO"

    # ── API ────────────────────────────────────────────────────────────
    api_keys: str = ""
    cors_allowed_origins: str = ""

    # ── MCP ────────────────────────────────────────────────────────────
    mcp_enabled: bool = False
    mcp_server_url: str = ""
    mcp_transport: MCPTransport = DEFAULT_MCP_TRANSPORT

    @field_validator("openai_base_url")
    @classmethod
    def validate_openai_base_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("openai_base_url must not be empty")
        stripped = v.strip()
        if not stripped.startswith(("http://", "https://")):
            msg = f"openai_base_url must start with http:// or https://, got '{v}'"
            raise ValueError(msg)
        return stripped.rstrip("/")

    @field_validator("openai_model")
    @classmethod
    def validate_openai_model(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("openai_model must not be empty")
        if not _OPENAI_MODEL_PATTERN.match(v):
            msg = (
                "openai_model must contain only letters, digits, dots, "
                f"underscores, and hyphens, got '{v}'"
            )
            raise ValueError(msg)
        return v

    @field_validator("openai_api_key", "anthropic_api_key", "tavily_api_key", mode="before")
    @classmethod
    def normalize_optional_secret(cls, v: object) -> object:
        """Treat unset/blank env values as missing optional secrets."""
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            msg = f"log_level must be one of {allowed}, got '{v}'"
            raise ValueError(msg)
        return upper

    @field_validator("agent_temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            msg = f"agent_temperature must be between 0.0 and 2.0, got {v}"
            raise ValueError(msg)
        return v

    @field_validator("agent_max_iterations")
    @classmethod
    def validate_max_iterations(cls, v: int) -> int:
        if v < 1:
            msg = f"agent_max_iterations must be >= 1, got {v}"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_provider_keys(self) -> "AppSettings":
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("openai_api_key is required when llm_provider is 'openai'")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("anthropic_api_key is required when llm_provider is 'anthropic'")
        return self

    def get_api_keys(self) -> set[str]:
        """Parse comma-separated API keys for route authentication."""
        if not self.api_keys.strip():
            return set()
        return {key.strip() for key in self.api_keys.split(",") if key.strip()}

    def get_cors_origins(self) -> list[str]:
        """Parse comma-separated CORS allowed origins."""
        if not self.cors_allowed_origins.strip():
            return []
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

    def get_secret(self, field: str) -> str:
        """Extract plain-text value from a whitelisted SecretStr field."""
        if field not in _SECRET_FIELDS:
            raise ValueError(f"Unknown secret field: {field}")
        value = getattr(self, field)
        if value is None:
            raise ValueError(f"Secret field '{field}' is not set")
        return value.get_secret_value()


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return singleton AppSettings instance.

    Cached so repeated calls across the process share one object.
    Call with ``get_settings.cache_clear()`` in tests to force reload.
    """
    return AppSettings()
