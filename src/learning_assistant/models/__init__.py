"""Shared data models — Pydantic contracts used across all modules."""

from learning_assistant.models.agent import AgentResponse, AgentState, ResponseMetadata
from learning_assistant.models.base import DomainModel
from learning_assistant.models.chat import ChatMessage, Conversation, MessageRole
from learning_assistant.models.document import DocumentChunk, PDFDocument
from learning_assistant.models.rag import (
    EmbeddingResult,
    RAGCitation,
    RAGResponse,
    RetrievedChunk,
    RetrievedContext,
)
from learning_assistant.models.search import SearchResponse, SearchResult
from learning_assistant.models.source import Source, SourceCitation, SourceType
from learning_assistant.models.tool import ToolCall, ToolDefinition, ToolResult

__all__ = [
    "AgentResponse",
    "AgentState",
    "ChatMessage",
    "Conversation",
    "DocumentChunk",
    "DomainModel",
    "EmbeddingResult",
    "MessageRole",
    "PDFDocument",
    "RAGCitation",
    "RAGResponse",
    "ResponseMetadata",
    "RetrievedChunk",
    "RetrievedContext",
    "SearchResponse",
    "SearchResult",
    "Source",
    "SourceCitation",
    "SourceType",
    "ToolCall",
    "ToolDefinition",
    "ToolResult",
]
