"""OpenAI-compatible LLM provider (OpenAI, MiMo Token Plan, etc.)."""

from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from learning_assistant.agent.llm.base import BaseLLM, LLMResponse


class OpenAICompatibleLLM(BaseLLM):
    """Chat completions via any OpenAI-compatible HTTP API."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        temperature: float = 0.2,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._temperature = temperature

    async def generate(self, messages: list[dict[str, str]]) -> LLMResponse:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self._temperature,
                stream=False,
            )
        except Exception as exc:
            raise RuntimeError(f"OpenAI API error: {exc}") from exc

        if not response.choices:
            raise RuntimeError("OpenAI API error: response contained no choices")

        choice = response.choices[0]
        content = choice.message.content or ""
        return LLMResponse(content=content, finish_reason=choice.finish_reason or "stop")

    async def stream_tokens(
        self, messages: list[dict[str, str]]
    ) -> AsyncIterator[str]:
        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self._temperature,
                stream=True,
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta is None or delta.content is None:
                    continue
                yield delta.content
        except Exception as exc:
            raise RuntimeError(f"OpenAI API error: {exc}") from exc
