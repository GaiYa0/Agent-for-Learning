"""Tests for ChatUseCase."""

import pytest

from learning_assistant.agent.planner import Planner
from learning_assistant.application.dto.chat_request import ChatRequest
from learning_assistant.application.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
)
from learning_assistant.application.usecases.chat_usecase import ChatUseCase
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM


@pytest.fixture()
def usecase() -> ChatUseCase:
    llm = MockLLM.with_react_sequence(
        ["Thought: Simple.\nFinal Answer: Hello there!"]
    )
    orch = AgentOrchestrator(ToolRegistry(), Planner(llm=llm))
    return ChatUseCase(orch)


class TestChatUseCase:
    @pytest.mark.asyncio
    async def test_success(self, usecase: ChatUseCase) -> None:
        req = ChatRequest(session_id="s1", message="Hi")
        result = await usecase.execute(req)
        assert result.success is True
        assert result.data is not None
        assert "Hello" in result.data.answer

    @pytest.mark.asyncio
    async def test_empty_message_rejected(self, usecase: ChatUseCase) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ChatRequest(session_id="s1", message="")
