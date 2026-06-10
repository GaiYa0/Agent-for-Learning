"""RAG-layer exception hierarchy."""


class RAGError(Exception):
    """Base for all RAG errors."""


class EmbeddingError(RAGError):
    """Raised when embedding fails."""


class VectorStoreError(RAGError):
    """Base for vector store errors."""


class RetrievalError(RAGError):
    """Raised when retrieval fails."""


class IndexingError(RAGError):
    """Raised when document indexing fails."""


class PipelineError(RAGError):
    """Raised when a pipeline stage fails."""
