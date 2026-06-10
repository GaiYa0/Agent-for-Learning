"""Tests for Planner streaming."""

import pytest

from learning_assistant.agent.planner import Planner
from learning_assistant.agent.state import AgentAction
from tests.mocks.mock_llm import MockLLM, MockLLMResponse


class TestPlannerStream:
    @pytest.mark.asyncio
    async def test_plan_stream_yields_tokens_then_action(self) -> None:
        llm = MockLLM([
            MockLLMResponse(
                content="Thought: Done.\nFinal Answer: Stream works."
            ),
        ])
        planner = Planner(llm=llm)
        items: list[str | AgentAction] = []
        async for item in planner.plan_stream(
            question="Q",
            tools_description="- t: d",
            history=[],
            observations="None.",
        ):
            items.append(item)

        assert items[:-1] == ["Thought: Done.\nFinal Answer: Stream works."]
        action = items[-1]
        assert isinstance(action, AgentAction)
        assert action.is_final is True
        assert "Stream works" in action.final_answer
