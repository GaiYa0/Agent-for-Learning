"""Streaming events emitted during agent execution."""

from dataclasses import dataclass, field
from typing import Literal

from learning_assistant.models.agent import ResponseMetadata
from learning_assistant.models.rag import RAGCitation

StreamEventKind = Literal["token", "tool_start", "tool_end", "done", "error"]


@dataclass
class StreamEvent:
    """Single event in a streaming agent response."""

    kind: StreamEventKind
    content: str = ""
    answer: str = ""
    tool_name: str = ""
    message: str = ""
    metadata: ResponseMetadata | None = None
    citations: list[RAGCitation] = field(default_factory=list)

    def to_sse_payload(self) -> dict[str, object]:
        """Serialize to JSON-compatible dict for SSE."""
        payload: dict[str, object] = {"type": self.kind}
        if self.kind == "token":
            payload["content"] = self.content
        elif self.kind == "tool_start":
            payload["tool_name"] = self.tool_name
            if self.content:
                payload["content"] = self.content
        elif self.kind == "tool_end":
            payload["tool_name"] = self.tool_name
            if self.content:
                payload["content"] = self.content
        elif self.kind == "done":
            payload["answer"] = self.answer
            if self.metadata is not None:
                payload["metadata"] = self.metadata.model_dump()
            if self.citations:
                payload["citations"] = [c.model_dump() for c in self.citations]
        elif self.kind == "error":
            payload["message"] = self.message
        return payload
