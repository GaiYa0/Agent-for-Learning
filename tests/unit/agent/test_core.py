"""Tests for ReActAgent — offline, all mocks."""

import pytest

from learning_assistant.agent.core import ReActAgent
from learning_assistant.agent.events import AgentFinished, ToolCalled, ToolFinished
from learning_assistant.agent.executor import ActionExecutor
from learning_assistant.agent.memory import ConversationMemory
from learning_assistant.agent.planner import Planner
from learning_assistant.tools.manager import ToolManager
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM
from tests.mocks.mock_tool import MockTool


def _build_agent(llm: MockLLM, tools: list[MockTool] | None = None) -> ReActAgent:
    registry = ToolRegistry()
    for t in (tools or []):
        registry.register(t)
    manager = ToolManager(registry)
    planner = Planner(llm=llm)
    executor = ActionExecutor(manager)
    tool_desc = "\n".join(
        f"- {t.name}: {t.description}" for t in (tools or [])
    )
    return ReActAgent(
        planner=planner,
        executor=executor,
        memory=ConversationMemory(),
        max_iterations=5,
        tools_description=tool_desc,
    )


class TestReActAgentSingleStep:
    @pytest.mark.asyncio
    async def test_direct_answer(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Simple question.\nFinal Answer: 42 is the answer."
        ])
        agent = _build_agent(llm)
        answer = await agent.run("What is 6x7?")
        assert answer == "42 is the answer."

    @pytest.mark.asyncio
    async def test_emits_agent_finished_event(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Done.\nFinal Answer: Yes."
        ])
        agent = _build_agent(llm)
        await agent.run("Q")
        events = agent.get_events()
        finished = [e for e in events if isinstance(e, AgentFinished)]
        assert len(finished) == 1


class TestReActAgentToolUse:
    @pytest.mark.asyncio
    async def test_tool_call_and_answer(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Need to use tool.\nAction: calc\nAction Input: 2+2",
            "Thought: Got result.\nFinal Answer: The answer is 4.",
        ])
        tool = MockTool(tool_name="calc", result_content="4")
        agent = _build_agent(llm, tools=[tool])
        answer = await agent.run("What is 2+2?")
        assert answer == "The answer is 4."
        assert tool.call_count == 1

    @pytest.mark.asyncio
    async def test_tool_failure_recovery(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Try tool.\nAction: bad\nAction Input: x",
            "Thought: Tool failed, I'll answer directly.\nFinal Answer: Fallback answer.",
        ])
        tool = MockTool.failing(name="bad", error="broken")
        agent = _build_agent(llm, tools=[tool])
        answer = await agent.run("Q")
        assert answer == "Fallback answer."

    @pytest.mark.asyncio
    async def test_emits_tool_events(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Use tool.\nAction: t\nAction Input: x",
            "Thought: Done.\nFinal Answer: ok.",
        ])
        tool = MockTool(tool_name="t", result_content="r")
        agent = _build_agent(llm, tools=[tool])
        await agent.run("Q")
        events = agent.get_events()
        assert any(isinstance(e, ToolCalled) for e in events)
        assert any(isinstance(e, ToolFinished) for e in events)


class TestReActAgentMultiStep:
    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Step 1.\nAction: a\nAction Input: x",
            "Thought: Step 2.\nAction: b\nAction Input: y",
            "Thought: Done.\nFinal Answer: Combined result.",
        ])
        ta = MockTool(tool_name="a", result_content="r1")
        tb = MockTool(tool_name="b", result_content="r2")
        agent = _build_agent(llm, tools=[ta, tb])
        answer = await agent.run("Q")
        assert answer == "Combined result."
        assert ta.call_count == 1
        assert tb.call_count == 1


class TestReActAgentMaxIterations:
    @pytest.mark.asyncio
    async def test_stops_at_max(self) -> None:
        steps = [
            f"Thought: Step {i}.\nAction: t\nAction Input: {i}"
            for i in range(10)
        ]
        llm = MockLLM.with_react_sequence(steps)
        tool = MockTool(tool_name="t", result_content="r")
        agent = _build_agent(llm, tools=[tool])
        agent._max_iterations = 3
        answer = await agent.run("Q")
        assert tool.call_count == 3
        assert "unable" in answer.lower()


class TestReActAgentParseError:
    @pytest.mark.asyncio
    async def test_recovers_from_parse_error(self) -> None:
        llm = MockLLM.with_react_sequence([
            "This is not valid ReAct output",
            "Thought: Fixed.\nFinal Answer: Recovered.",
        ])
        agent = _build_agent(llm)
        answer = await agent.run("Q")
        assert answer == "Recovered."


class TestReActAgentMemory:
    @pytest.mark.asyncio
    async def test_memory_populated(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Done.\nFinal Answer: ok."
        ])
        agent = _build_agent(llm)
        await agent.run("Test question")
        mem = agent.get_memory()
        assert mem.message_count() >= 2
