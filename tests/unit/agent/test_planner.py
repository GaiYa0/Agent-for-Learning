"""Tests for Planner."""

import pytest

from learning_assistant.agent.planner import Planner
from learning_assistant.agent.state import AgentAction
from tests.mocks.mock_llm import MockLLM, MockLLMResponse


@pytest.fixture()
def planner() -> Planner:
    llm = MockLLM([
        MockLLMResponse(
            content="Thought: Need to search.\nAction: search\nAction Input: AI"
        ),
        MockLLMResponse(
            content="Thought: Got it.\nFinal Answer: AI is artificial intelligence."
        ),
    ])
    return Planner(llm=llm)


class TestPlanner:
    @pytest.mark.asyncio
    async def test_plan_returns_action(self, planner: Planner) -> None:
        action = await planner.plan(
            question="What is AI?",
            tools_description="- search: search web",
            history=[],
            observations="None.",
        )
        assert isinstance(action, AgentAction)
        assert action.action == "search"
        assert action.is_final is False

    @pytest.mark.asyncio
    async def test_plan_final_answer(self, planner: Planner) -> None:
        await planner.plan(
            question="Q", tools_description="- t: d", history=[], observations="None."
        )
        action = await planner.plan(
            question="Q", tools_description="- t: d", history=[], observations="Obs."
        )
        assert action.is_final is True
        assert "artificial intelligence" in action.final_answer

    @pytest.mark.asyncio
    async def test_plan_with_context(self, planner: Planner) -> None:
        action = await planner.plan(
            question="Q",
            tools_description="- t: d",
            history=[],
            observations="None.",
            context="Some context.",
        )
        assert action is not None
