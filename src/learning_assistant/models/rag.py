"""RAG-specific data models."""

from datetime import UTC, datetime

from pydantic import Field

from learning_assistant.models.base import DomainModel


class EmbeddingResult(DomainModel):
    """Result of embedding a piece of text (for embeddings layer)."""

    text: str
    embedding: list[float]
    model: str = ""


class RetrievedChunk(DomainModel):
    """A chunk retrieved from the vector store."""

    content: str
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, str] = Field(default_factory=dict)
    chunk_id: str = ""
    source: str = ""
    page: int = Field(ge=0, default=0, description="0 means unknown or N/A for web")


class RetrievedContext(DomainModel):
    """Aggregated context from retrieval."""

    chunks: list[RetrievedChunk] = Field(default_factory=list)
    query: str = ""
    retrieval_time_ms: int = Field(ge=0, default=0)

    def as_text(self, separator: str = "\n\n") -> str:
        return separator.join(c.content for c in self.chunks)

    def sources(self) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for c in self.chunks:
            if c.source and c.source not in seen:
                seen.add(c.source)
                result.append(c.source)
        return result


class RAGCitation(DomainModel):
    """Numbered citation for a retrieved chunk (RAG pipeline)."""

    index: int = Field(ge=1)
    source: str = ""
    page: int = Field(ge=0, default=0, description="0 means unknown or N/A for web")
    chunk_id: str = ""
    snippet: str = ""


# Backward-compatible alias — prefer RAGCitation in new code
Citation = RAGCitation


class RAGResponse(DomainModel):
    """Final response from the RAG pipeline."""

    answer: str
    citations: list[RAGCitation] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    retrieved_chunks: int = 0
    retrieval_time_ms: int = Field(ge=0, default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
