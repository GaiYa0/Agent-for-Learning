"""RAG API schemas."""

from pydantic import BaseModel, Field

from learning_assistant.models.rag import RAGCitation


class RAGChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    top_k: int = Field(ge=1, le=20, default=5)


class RAGChatResponseDTO(BaseModel):
    answer: str
    citations: list[RAGCitation] = []
    retrieved_chunks: int = 0
    retrieval_time_ms: int = 0
