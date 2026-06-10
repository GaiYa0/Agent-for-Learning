"""MCP layer — Model Context Protocol integration."""

from learning_assistant.mcp.client.base import (
    BaseMCPClient,
    MCPPrompt,
    MCPResource,
    MCPToolDef,
    MCPToolResult,
)
from learning_assistant.mcp.client.mcp_client import MCPClient
from learning_assistant.mcp.discovery.capability_manager import CapabilityManager
from learning_assistant.mcp.factories.mcp_factory import MCPFactory
from learning_assistant.mcp.tool_provider import MCPToolProvider

__all__ = [
    "BaseMCPClient",
    "CapabilityManager",
    "MCPClient",
    "MCPFactory",
    "MCPPrompt",
    "MCPResource",
    "MCPToolDef",
    "MCPToolProvider",
    "MCPToolResult",
]
