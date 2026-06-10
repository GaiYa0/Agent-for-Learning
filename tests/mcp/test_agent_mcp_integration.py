"""Agent + MCP integration tests — all offline."""

import pytest

from learning_assistant.agent.core import ReActAgent
from learning_assistant.agent.executor import ActionExecutor
from learning_assistant.agent.memory import ConversationMemory
from learning_assistant.agent.planner import Planner
from learning_assistant.mcp.client.base import MCPToolDef, MCPToolResult
from learning_assistant.mcp.discovery.capability_manager import CapabilityManager
from learning_assistant.mcp.tool_provider import MCPToolProvider
from learning_assistant.tools.manager import ToolManager
from learning_assistant.tools.registry import ToolRegistry
from tests.mcp.mock_mcp_server import MockMCPServer
from tests.mocks.mock_llm import MockLLM
from tests.mocks.mock_tool import MockTool


async def _build_agent_with_mcp(
    llm: MockLLM,
    local_tools: list[MockTool] | None = None,
    mcp_server: MockMCPServer | None = None,
) -> tuple[ReActAgent, MCPToolProvider | None]:
    registry = ToolRegistry()
    for t in local_tools or []:
        registry.register(t)

    mcp_provider = None
    if mcp_server:
        mcp_provider = MCPToolProvider(mcp_server, CapabilityManager())
        await mcp_provider.discover_tools()
        mcp_provider.register_to(registry)

    manager = ToolManager(registry)
    planner = Planner(llm=llm)
    executor = ActionExecutor(manager)
    tool_desc = "\n".join(
        f"- {t.name}: {t.description}" for t in registry.list_tools()
    )

    agent = ReActAgent(
        planner=planner,
        executor=executor,
        memory=ConversationMemory(),
        max_iterations=5,
        tools_description=tool_desc,
    )
    return agent, mcp_provider


class TestAgentMCPIntegration:
    @pytest.mark.asyncio
    async def test_agent_discovers_mcp_tools(self) -> None:
        server = MockMCPServer()
        server.add_tool(MCPToolDef(name="mcp_tool", description="MCP tool"))
        provider = MCPToolProvider(server, CapabilityManager())
        tools = await provider.discover_tools()
        assert len(tools) == 1
        assert tools[0].name == "mcp_tool"

    @pytest.mark.asyncio
    async def test_agent_calls_mcp_tool(self) -> None:
        server = MockMCPServer()
        server.add_tool(
            MCPToolDef(name="mcp_calc", description="MCP calculator"),
            MCPToolResult(content="42"),
        )
        provider = MCPToolProvider(server, CapabilityManager())
        await provider.discover_tools()
        result = await provider.call_tool("mcp_calc", {"input": "6*7"})
        assert result.is_success()
        assert result.content == "42"

    @pytest.mark.asyncio
    async def test_agent_handles_mcp_tool_failure(self) -> None:
        server = MockMCPServer()
        server.add_tool(
            MCPToolDef(name="bad_tool", description="Bad tool"),
            MCPToolResult(content="error occurred", is_error=True),
        )
        provider = MCPToolProvider(server, CapabilityManager())
        await provider.discover_tools()
        result = await provider.call_tool("bad_tool", {})
        assert result.is_failure()

    @pytest.mark.asyncio
    async def test_agent_with_local_and_mcp_tools(self) -> None:
        local = MockTool(tool_name="local_tool", result_content="local_result")
        server = MockMCPServer()
        server.add_tool(
            MCPToolDef(name="remote_tool", description="Remote MCP tool"),
            MCPToolResult(content="mcp_result"),
        )
        llm = MockLLM.with_react_sequence([
            "Thought: Use MCP.\nAction: mcp_default_remote_tool\nAction Input: {}",
            "Thought: Done.\nFinal Answer: Combined answer.",
        ])
        agent, provider = await _build_agent_with_mcp(
            llm, local_tools=[local], mcp_server=server
        )
        assert provider is not None
        answer = await agent.run("Q")
        assert answer == "Combined answer."
        assert len(server.call_log) == 1
        assert server.call_log[0][0] == "remote_tool"

    @pytest.mark.asyncio
    async def test_mcp_provider_tool_definitions(self) -> None:
        server = MockMCPServer()
        server.add_tool(MCPToolDef(name="t1", description="d1", input_schema={"type": "object"}))
        provider = MCPToolProvider(server, CapabilityManager())
        await provider.discover_tools()
        defs = provider.get_tool_definitions()
        assert defs[0]["name"] == "t1"
