"""MCP JSON-RPC response parsing helpers."""

from typing import Any

from learning_assistant.mcp.exceptions import MCPError


def unwrap_result(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract the MCP result object from a transport response."""
    if "error" in payload:
        error = payload["error"]
        if isinstance(error, dict):
            message = error.get("message", str(error))
        else:
            message = str(error)
        raise MCPError(message)
    if "result" in payload:
        result = payload["result"]
        if isinstance(result, dict):
            return result
        return {"value": result}
    return payload


def parse_tool_content(result: dict[str, Any]) -> tuple[str, bool]:
    """Parse tools/call result into plain text and error flag."""
    is_error = bool(result.get("isError", False))
    content = result.get("content", "")
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            elif isinstance(block, dict):
                parts.append(str(block.get("text", block.get("content", ""))))
        content = "\n".join(parts)
    elif not isinstance(content, str):
        content = str(content)
    return content, is_error


def parse_resource_content(result: dict[str, Any]) -> str:
    """Parse resources/read result into text content."""
    if "content" in result and isinstance(result["content"], str):
        return result["content"]
    contents = result.get("contents", [])
    if isinstance(contents, list) and contents:
        first = contents[0]
        if isinstance(first, dict):
            return str(first.get("text", first.get("content", "")))
    return ""
