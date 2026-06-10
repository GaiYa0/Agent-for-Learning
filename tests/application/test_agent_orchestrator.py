"""Tests for AgentOrchestrator."""

import pytest

from learning_assistant.agent.planner import Planner
from learning_assistant.application.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
)
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM
from tests.mocks.mock_tool import MockTool


@pytest.fixture()
def orchestrator() -> AgentOrchestrator:
    llm = MockLLM.with_react_sequence(
        ["Thought: Done.\nFinal Answer: 42"]
    )
    registry = ToolRegistry()
    registry.register(MockTool(tool_name="calc", result_content="42"))
    return AgentOrchestrator(registry, Planner(llm=llm))


class TestAgentOrchestrator:
    @pytest.mark.asyncio
    async def test_run(self, orchestrator: AgentOrchestrator) -> None:
        response = await orchestrator.run("What is 6x7?")
        assert "42" in response.answer

    @pytest.mark.asyncio
    async def test_run_with_context(self, orchestrator: AgentOrchestrator) -> None:
        response = await orchestrator.run("Q", context="Some context.")
        assert response.answer

    def test_build_agent(self, orchestrator: AgentOrchestrator) -> None:
        agent = orchestrator.build_agent()
        assert agent is not None
