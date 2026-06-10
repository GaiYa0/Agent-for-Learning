"""Integration tests for the full ReAct agent pipeline — all offline."""

import pytest

from learning_assistant.agent.core import ReActAgent
from learning_assistant.agent.executor import ActionExecutor
from learning_assistant.agent.memory import ConversationMemory
from learning_assistant.agent.planner import Planner
from learning_assistant.tools.manager import ToolManager
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM
from tests.mocks.mock_search import MockSearchProvider
from tests.mocks.mock_tool import MockTool


def _build_full_agent(
    llm: MockLLM, tools: list[MockTool]
) -> ReActAgent:
    registry = ToolRegistry()
    for t in tools:
        registry.register(t)
    manager = ToolManager(registry)
    planner = Planner(llm=llm)
    executor = ActionExecutor(manager)
    tool_desc = "\n".join(f"- {t.name}: {t.description}" for t in tools)
    return ReActAgent(
        planner=planner,
        executor=executor,
        memory=ConversationMemory(),
        max_iterations=10,
        tools_description=tool_desc,
    )


class TestQuestionAnswering:
    @pytest.mark.asyncio
    async def test_simple_qa(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: I know this.\nFinal Answer: Python is a programming language."
        ])
        agent = _build_full_agent(llm, [])
        answer = await agent.run("What is Python?")
        assert "Python" in answer

    @pytest.mark.asyncio
    async def test_qa_with_tool(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Let me calculate.\nAction: calculator\nAction Input: 15 * 23",
            "Thought: Got it.\nFinal Answer: 15 times 23 is 345.",
        ])
        calc = MockTool(tool_name="calculator", result_content="345")
        agent = _build_full_agent(llm, [calc])
        answer = await agent.run("What is 15 * 23?")
        assert "345" in answer


class TestSearchIntegration:
    @pytest.mark.asyncio
    async def test_search_and_answer(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Need to search.\nAction: web_search\nAction Input: Python history",
            "Thought: Found info.\nFinal Answer: Python was created by Guido van Rossum.",
        ])
        search_tool = MockTool(
            tool_name="web_search",
            result_content="Python was created by Guido van Rossum in 1991.",
        )
        agent = _build_full_agent(llm, [search_tool])
        answer = await agent.run("Who created Python?")
        assert "Guido" in answer


class TestPDFAnalysis:
    @pytest.mark.asyncio
    async def test_pdf_read_and_summarize(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Read the PDF.\nAction: pdf_reader\nAction Input: /tmp/course.pdf",
            "Thought: Got content.\nFinal Answer: The PDF covers machine learning basics.",
        ])
        pdf_tool = MockTool(
            tool_name="pdf_reader",
            result_content="Chapter 1: Introduction to Machine Learning...",
        )
        agent = _build_full_agent(llm, [pdf_tool])
        answer = await agent.run("Summarize the PDF")
        assert "machine learning" in answer.lower()


class TestMultiToolCollaboration:
    @pytest.mark.asyncio
    async def test_search_then_calculate(self) -> None:
        llm = MockLLM.with_react_sequence([
            "Thought: Search first.\nAction: search\nAction Input: GDP 2023",
            "Thought: Now calculate.\nAction: calc\nAction Input: 25000 / 330",
            "Thought: Done.\nFinal Answer: Per capita GDP is approximately 75.76K.",
        ])
        search = MockTool(tool_name="search", result_content="US GDP 2023: 25 trillion")
        calc = MockTool(tool_name="calc", result_content="75.76")
        agent = _build_full_agent(llm, [search, calc])
        answer = await agent.run("US per capita GDP?")
        assert "75.76" in answer
        assert search.call_count == 1
        assert calc.call_count == 1


class TestMockSearchProvider:
    @pytest.mark.asyncio
    async def test_provider_with_results(self) -> None:
        provider = MockSearchProvider.with_results(["AI", "ML"])
        resp = await provider.search("test")
        assert resp.result_count() == 2

    @pytest.mark.asyncio
    async def test_provider_empty(self) -> None:
        provider = MockSearchProvider.empty()
        resp = await provider.search("test")
        assert resp.result_count() == 0

    @pytest.mark.asyncio
    async def test_provider_failure(self) -> None:
        provider = MockSearchProvider.failing()
        with pytest.raises(ConnectionError):
            await provider.search("test")
