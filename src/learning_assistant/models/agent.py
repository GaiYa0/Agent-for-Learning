"""Agent state and response models.

Domain-layer contracts for agent I/O. The runtime reasoning loop uses
``learning_assistant.agent.state.AgentRuntimeState`` (dataclass) instead of
``AgentState`` for mutable per-run state.
"""

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import Field

from learning_assistant.models.base import DomainModel
from learning_assistant.models.chat import Conversation
from learning_assistant.models.source import Source, SourceCitation


class AgentState(DomainModel):
    """Mutable state tracked across agent reasoning iterations."""

    conversation: Conversation = Field(default_factory=Conversation)
    iteration: int = Field(ge=0, default=0)
    max_iterations: int = Field(ge=1, default=5)
    tools_used: list[str] = Field(default_factory=list)

    def can_continue(self) -> bool:
        return self.iteration < self.max_iterations

    def increment_iteration(self) -> None:
        self.iteration += 1


class ResponseMetadata(DomainModel):
    """Metadata about how an agent response was produced."""

    iterations: int = Field(ge=0, default=0)
    tools_used: list[str] = Field(default_factory=list)
    total_duration_ms: int = Field(ge=0, default=0)
    retrieval_time_ms: int = Field(ge=0, default=0)
    model: str = ""


class AgentResponse(DomainModel):
    """The final answer returned by the agent."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    answer: str
    citations: list[SourceCitation] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    metadata: ResponseMetadata = Field(
        default_factory=lambda: ResponseMetadata(iterations=0)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
