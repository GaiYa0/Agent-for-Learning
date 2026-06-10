"""Tool definition, call, and result models."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import Field

from learning_assistant.models.base import DomainModel


class ToolDefinition(DomainModel):
    """Describes a tool that the agent can invoke."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)
    category: str = Field(min_length=1)


class ToolCall(DomainModel):
    """Records a request to invoke a tool."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ToolResult(DomainModel):
    """The outcome of a tool execution."""

    tool_call_id: str
    success: bool
    content: str = ""
    error: str | None = None
    duration_ms: int = Field(ge=0, default=0)

    def is_success(self) -> bool:
        return self.success

    def is_failure(self) -> bool:
        return not self.success
