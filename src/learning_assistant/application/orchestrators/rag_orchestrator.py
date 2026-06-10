"""RAG orchestrator — coordinates retrieval, indexing, and embedding."""

from learning_assistant.models.rag import RetrievedContext
from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.indexing.document_indexer import DocumentIndexer
from learning_assistant.rag.pipelines.citation_pipeline import CitationPipeline
from learning_assistant.rag.pipelines.retrieval_pipeline import RetrievalPipeline
from learning_assistant.rag.vectorstores.base import VectorStore


class RAGOrchestrator:
    """Coordinates RAG components."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        retrieval_pipeline: RetrievalPipeline,
        citation_pipeline: CitationPipeline | None = None,
    ) -> None:
        self._embedding = embedding_provider
        self._store = vector_store
        self._retrieval = retrieval_pipeline
        self._citations = citation_pipeline or CitationPipeline()
        self._indexer = DocumentIndexer(embedding_provider, vector_store)

    async def retrieve(self, query: str, top_k: int = 5) -> RetrievedContext:
        return await self._retrieval.run(query, top_k)

    async def index_text(self, text: str, source: str = "") -> int:
        return await self._indexer.index_text(text, source)

    def get_indexer(self) -> DocumentIndexer:
        return self._indexer

    def get_citation_pipeline(self) -> CitationPipeline:
        return self._citations
