"""Tests for use case error paths."""

import pytest

from learning_assistant.agent.planner import Planner
from learning_assistant.application.dto.chat_request import ChatRequest
from learning_assistant.application.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
)
from learning_assistant.application.usecases.chat_usecase import ChatUseCase
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM


@pytest.mark.asyncio
async def test_chat_usecase_agent_error() -> None:
    llm = MockLLM.with_error("LLM failure")
    orch = AgentOrchestrator(ToolRegistry(), Planner(llm=llm))
    usecase = ChatUseCase(orch)
    req = ChatRequest(session_id="s1", message="Hello")
    result = await usecase.execute(req)
    assert result.success is False
    assert result.error is not None
