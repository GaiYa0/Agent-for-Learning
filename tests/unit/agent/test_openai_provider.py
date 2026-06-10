"""Tests for OpenAICompatibleLLM."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from learning_assistant.agent.llm.openai_provider import OpenAICompatibleLLM


def _make_chunk(content: str | None) -> MagicMock:
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta.content = content
    return chunk


def _make_empty_choices_chunk() -> MagicMock:
    chunk = MagicMock()
    chunk.choices = []
    return chunk


class TestOpenAICompatibleLLM:
    @pytest.mark.asyncio
    async def test_generate_returns_content(self) -> None:
        llm = OpenAICompatibleLLM(
            api_key="tp-test",
            model="mimo-v2.5-pro",
            base_url="https://token-plan-cn.xiaomimimo.com/v1",
        )
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello"
        mock_response.choices[0].finish_reason = "stop"

        with patch.object(
            llm._client.chat.completions,
            "create",
            new=AsyncMock(return_value=mock_response),
        ) as mock_create:
            result = await llm.generate([{"role": "user", "content": "hi"}])

        assert result.content == "Hello"
        assert result.finish_reason == "stop"
        mock_create.assert_awaited_once()
        call_kwargs = mock_create.await_args.kwargs
        assert call_kwargs["stream"] is False
        assert call_kwargs["model"] == "mimo-v2.5-pro"

    @pytest.mark.asyncio
    async def test_generate_wraps_api_errors(self) -> None:
        llm = OpenAICompatibleLLM(
            api_key="tp-test",
            model="mimo-v2.5-pro",
            base_url="https://token-plan-cn.xiaomimimo.com/v1",
        )
        with patch.object(
            llm._client.chat.completions,
            "create",
            new=AsyncMock(side_effect=RuntimeError("network down")),
        ):
            with pytest.raises(RuntimeError, match="OpenAI API error"):
                await llm.generate([{"role": "user", "content": "hi"}])

    @pytest.mark.asyncio
    async def test_stream_tokens_yields_deltas(self) -> None:
        llm = OpenAICompatibleLLM(
            api_key="tp-test",
            model="mimo-v2.5-pro",
            base_url="https://token-plan-cn.xiaomimimo.com/v1",
        )

        async def fake_stream():
            for piece in ["Hel", "lo"]:
                yield _make_chunk(piece)
            yield _make_chunk(None)

        with patch.object(
            llm._client.chat.completions,
            "create",
            new=AsyncMock(return_value=fake_stream()),
        ) as mock_create:
            chunks = [
                token
                async for token in llm.stream_tokens(
                    [{"role": "user", "content": "hi"}]
                )
            ]

        assert chunks == ["Hel", "lo"]
        assert mock_create.await_args.kwargs["stream"] is True

    @pytest.mark.asyncio
    async def test_stream_tokens_skips_empty_choices_chunks(self) -> None:
        llm = OpenAICompatibleLLM(
            api_key="tp-test",
            model="mimo-v2.5-pro",
            base_url="https://token-plan-cn.xiaomimimo.com/v1",
        )

        async def fake_stream():
            yield _make_chunk("Hel")
            yield _make_empty_choices_chunk()
            yield _make_chunk("lo")
            yield _make_chunk(None)

        with patch.object(
            llm._client.chat.completions,
            "create",
            new=AsyncMock(return_value=fake_stream()),
        ):
            chunks = [
                token
                async for token in llm.stream_tokens(
                    [{"role": "user", "content": "hi"}]
                )
            ]

        assert chunks == ["Hel", "lo"]
