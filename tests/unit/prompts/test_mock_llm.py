"""Tests for MockLLM."""

import pytest

from tests.mocks.mock_llm import MockLLM, MockLLMResponse


class TestMockLLM:
    @pytest.mark.asyncio
    async def test_fixed_reply(self) -> None:
        llm = MockLLM.with_fixed_reply("Hello!")
        resp = await llm.generate([{"role": "user", "content": "Hi"}])
        assert resp.content == "Hello!"
        assert llm.call_count == 1

    @pytest.mark.asyncio
    async def test_react_sequence(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: I need to search\nAction: search\nAction Input: AI",
            "Thought: I have info\nAction: finish\nAction Input: answer",
        ])
        resp1 = await llm.generate([])
        assert "Thought:" in resp1.content
        resp2 = await llm.generate([])
        assert "finish" in resp2.content

    @pytest.mark.asyncio
    async def test_error_response(self) -> None:
        llm = MockLLM.with_error("API error")
        with pytest.raises(RuntimeError, match="API error"):
            await llm.generate([])

    @pytest.mark.asyncio
    async def test_exhausted_responses(self) -> None:
        llm = MockLLM.with_fixed_reply("only one")
        await llm.generate([])
        resp = await llm.generate([])
        assert "No more mock responses" in resp.content

    @pytest.mark.asyncio
    async def test_call_log(self) -> None:
        llm = MockLLM.with_fixed_reply("ok")
        messages = [{"role": "user", "content": "test"}]
        await llm.generate(messages)
        assert len(llm.call_log) == 1
        assert llm.call_log[0] == messages

    def test_reset(self) -> None:
        llm = MockLLM.with_fixed_reply("ok")
        llm.reset()
        assert llm.call_count == 0
        assert llm.call_log == []

    def test_add_response(self) -> None:
        llm = MockLLM()
        llm.add_response(MockLLMResponse(content="added"))
        assert len(llm._responses) == 1
