"""Tests for CapabilityManager."""

from learning_assistant.mcp.client.base import MCPPrompt, MCPResource, MCPToolDef
from learning_assistant.mcp.discovery.capability_manager import CapabilityManager


class TestCapabilityManager:
    def test_register_tools(self) -> None:
        mgr = CapabilityManager()
        tools = [
            MCPToolDef(name="t1", description="d1"),
            MCPToolDef(name="t2", description="d2"),
        ]
        mgr.register_tools(tools, server_id="s1")
        assert mgr.tool_count() == 2

    def test_register_resources(self) -> None:
        mgr = CapabilityManager()
        resources = [MCPResource(uri="file:///a", name="a")]
        mgr.register_resources(resources)
        assert mgr.resource_count() == 1

    def test_register_prompts(self) -> None:
        mgr = CapabilityManager()
        prompts = [MCPPrompt(name="p1", description="d1")]
        mgr.register_prompts(prompts)
        assert mgr.prompt_count() == 1

    def test_remove_server(self) -> None:
        mgr = CapabilityManager()
        tools = [MCPToolDef(name="t1", description="d1")]
        mgr.register_tools(tools, server_id="s1")
        mgr.remove_server("s1")
        assert mgr.tool_count() == 0

    def test_registries_accessible(self) -> None:
        mgr = CapabilityManager()
        assert mgr.tool_registry is not None
        assert mgr.resource_registry is not None
        assert mgr.prompt_registry is not None
