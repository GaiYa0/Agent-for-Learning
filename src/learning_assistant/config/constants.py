"""System-wide constants. No business logic, no side effects."""

from typing import Final, Literal

LLMProvider = Literal["openai", "anthropic"]
SearchProvider = Literal["tavily", "duckduckgo"]
MCPTransport = Literal["http", "sse", "stdio"]
Environment = Literal["development", "testing", "staging", "production"]

DEFAULT_OPENAI_BASE_URL: Final[str] = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_MIMO_MODEL: Final[str] = "mimo-v2.5-pro"
DEFAULT_MODEL: Final[str] = DEFAULT_MIMO_MODEL
DEFAULT_MAX_ITERATIONS: Final[int] = 5
DEFAULT_TEMPERATURE: Final[float] = 0.2
DEFAULT_LLM_PROVIDER: Final[LLMProvider] = "openai"
DEFAULT_SEARCH_PROVIDER: Final[SearchProvider] = "tavily"
DEFAULT_MCP_TRANSPORT: Final[MCPTransport] = "http"

SUPPORTED_LLM_PROVIDERS: Final[tuple[str, ...]] = ("openai", "anthropic")
SUPPORTED_SEARCH_PROVIDERS: Final[tuple[str, ...]] = ("tavily", "duckduckgo")
