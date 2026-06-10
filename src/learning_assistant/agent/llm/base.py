"""Abstract LLM interface — agents depend on this, never on a concrete SDK."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[dict[str, str]] = field(default_factory=list)
    finish_reason: str = "stop"


class BaseLLM(ABC):
    """Provider-agnostic language model interface."""

    @abstractmethod
    async def generate(self, messages: list[dict[str, str]]) -> LLMResponse:
        ...

    async def generate_structured(
        self, messages: list[dict[str, str]], schema: dict[str, object]
    ) -> dict[str, object]:
        resp = await self.generate(messages)
        import json

        result: dict[str, object] = json.loads(resp.content)
        return result

    async def stream(
        self, messages: list[dict[str, str]]
    ) -> str:
        resp = await self.generate(messages)
        return resp.content

    async def stream_tokens(
        self, messages: list[dict[str, str]]
    ) -> AsyncIterator[str]:
        """Yield text chunks; default falls back to a single full response."""
        content = await self.stream(messages)
        yield content
