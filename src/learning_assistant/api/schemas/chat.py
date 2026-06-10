"""Chat API schemas."""

from pydantic import BaseModel, Field

from learning_assistant.models.agent import ResponseMetadata
from learning_assistant.models.rag import RAGCitation


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, examples=["session-123"])
    message: str = Field(min_length=1, examples=["What is Python?"])
    use_rag: bool = Field(default=False, examples=[False])


class ResponseMetadataDTO(ResponseMetadata):
    """API schema for response metadata (shared with domain model)."""


class ChatResponseDTO(BaseModel):
    answer: str
    citations: list[RAGCitation] = []
    metadata: ResponseMetadataDTO = Field(default_factory=ResponseMetadataDTO)
