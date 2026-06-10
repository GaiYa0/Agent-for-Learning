"""Tests for BaseLLM — offline, mock only."""

import pytest

from learning_assistant.agent.llm.base import BaseLLM, LLMResponse
from tests.mocks.mock_llm import MockLLM


class TestBaseLLMInterface:
    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            BaseLLM()  # type: ignore[abstract]


class TestLLMResponse:
    def test_create(self) -> None:
        resp = LLMResponse(content="hello")
        assert resp.content == "hello"
        assert resp.tool_calls == []
        assert resp.finish_reason == "stop"

    def test_with_tool_calls(self) -> None:
        resp = LLMResponse(
            content="",
            tool_calls=[{"name": "t", "arguments": "{}"}],
        )
        assert len(resp.tool_calls) == 1


class TestMockLLMExtended:
    @pytest.mark.asyncio
    async def test_generate(self) -> None:
        llm = MockLLM.with_fixed_reply("ok")
        resp = await llm.generate([{"role": "user", "content": "hi"}])
        assert resp.content == "ok"
        assert resp.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_generate_structured(self) -> None:
        llm = MockLLM.with_fixed_reply('{"key": "value"}')
        result = await llm.generate_structured(
            [{"role": "user", "content": "hi"}], {}
        )
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_stream(self) -> None:
        llm = MockLLM.with_fixed_reply("streamed text")
        result = await llm.stream([{"role": "user", "content": "hi"}])
        assert result == "streamed text"
