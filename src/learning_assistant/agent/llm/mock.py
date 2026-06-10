"""Mock LLM for development and offline testing."""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from learning_assistant.agent.llm.base import BaseLLM, LLMResponse


@dataclass
class MockLLMResponse:
    content: str
    tool_calls: list[dict[str, str]] = field(default_factory=list)
    finish_reason: str = "stop"


class MockLLM(BaseLLM):
    """Returns pre-configured responses in sequence."""

    def __init__(
        self,
        responses: list[MockLLMResponse] | None = None,
        *,
        raise_on_generate: str | None = None,
    ) -> None:
        self._responses = responses or []
        self._call_count = 0
        self.call_log: list[list[dict[str, str]]] = []
        self._raise_on_generate = raise_on_generate

    def add_response(self, response: MockLLMResponse) -> None:
        self._responses.append(response)

    async def generate(self, messages: list[dict[str, str]]) -> LLMResponse:
        if self._raise_on_generate is not None:
            raise RuntimeError(self._raise_on_generate)
        self.call_log.append(messages)
        if self._call_count >= len(self._responses):
            return LLMResponse(content="No more mock responses configured.")
        resp = self._responses[self._call_count]
        self._call_count += 1
        return LLMResponse(
            content=resp.content,
            tool_calls=resp.tool_calls,
            finish_reason=resp.finish_reason,
        )

    async def stream_tokens(
        self, messages: list[dict[str, str]]
    ) -> AsyncIterator[str]:
        resp = await self.generate(messages)
        yield resp.content

    def reset(self) -> None:
        self._call_count = 0
        self.call_log.clear()

    @property
    def call_count(self) -> int:
        return self._call_count

    @classmethod
    def with_fixed_reply(cls, content: str) -> "MockLLM":
        return cls([MockLLMResponse(content=content)])

    @classmethod
    def with_react_sequence(cls, steps: list[str]) -> "MockLLM":
        return cls([MockLLMResponse(content=step) for step in steps])

    @classmethod
    def with_error(cls, error_msg: str = "API error") -> "MockLLM":
        return cls(raise_on_generate=error_msg)
