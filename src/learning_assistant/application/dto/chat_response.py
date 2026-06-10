"""Chat response DTO."""

from pydantic import BaseModel, Field

from learning_assistant.models.agent import ResponseMetadata
from learning_assistant.models.rag import RAGCitation


class ChatResponse(BaseModel):
    answer: str
    citations: list[RAGCitation] = Field(default_factory=list)
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)
