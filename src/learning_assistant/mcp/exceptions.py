"""MCP-layer exception hierarchy."""


class MCPError(Exception):
    """Base for all MCP errors."""


class MCPConnectionError(MCPError):
    """Raised when MCP connection fails."""


class MCPToolError(MCPError):
    """Raised when MCP tool execution fails."""


class MCPTimeoutError(MCPError):
    """Raised when MCP operation times out."""


class MCPDiscoveryError(MCPError):
    """Raised when server discovery fails."""


class MCPResourceError(MCPError):
    """Raised when resource retrieval fails."""


class MCPPromptError(MCPError):
    """Raised when prompt retrieval fails."""
