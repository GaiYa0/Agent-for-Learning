"""RAG state — manages RAG-specific UI state."""

from dataclasses import dataclass, field

from learning_assistant.frontend.state.chat_state import ChatState
from learning_assistant.models.rag import RAGCitation


@dataclass
class RAGState(ChatState):
    citations: list[RAGCitation] = field(default_factory=list)
    retrieved_chunks: int = 0
    retrieval_time_ms: int = 0

    def set_citations(self, citations: list[dict[str, object]]) -> None:
        parsed: list[RAGCitation] = []
        for i, raw in enumerate(citations):
            data = dict(raw)
            if "index" not in data:
                data["index"] = i + 1
            parsed.append(RAGCitation.model_validate(data))
        self.citations = parsed

    def clear(self) -> None:
        super().clear()
        self.citations.clear()
        self.retrieved_chunks = 0
        self.retrieval_time_ms = 0
