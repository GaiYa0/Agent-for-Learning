"""Unified exception hierarchy for all services."""


class ServiceError(Exception):
    """Base for all service-layer errors."""


class PDFError(ServiceError):
    """Base for PDF-related errors."""


class PDFReadError(PDFError):
    """Raised when a PDF cannot be read."""


class PDFEmptyError(PDFError):
    """Raised when a PDF has no extractable content."""


class ChunkError(ServiceError):
    """Raised when text chunking fails."""


class SearchError(ServiceError):
    """Base for search-related errors."""


class ProviderError(SearchError):
    """Raised when a search provider fails."""
