"""Service layer — PDF parsing, web search, and shared abstractions."""

from learning_assistant.services.base import BaseService
from learning_assistant.services.exceptions import (
    ChunkError,
    PDFEmptyError,
    PDFError,
    PDFReadError,
    ProviderError,
    SearchError,
    ServiceError,
)
from learning_assistant.services.factory import ServiceFactory
from learning_assistant.services.pdf.pdf_service import PDFService
from learning_assistant.services.search.search_service import SearchService

__all__ = [
    "BaseService",
    "ChunkError",
    "PDFEmptyError",
    "PDFError",
    "PDFReadError",
    "PDFService",
    "ProviderError",
    "SearchError",
    "SearchService",
    "ServiceError",
    "ServiceFactory",
]
