"""Document indexer — orchestrates chunking, metadata, embedding, and storage."""

from learning_assistant.models.document import DocumentChunk, PDFDocument
from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.indexing.chunk_processor import ChunkProcessor
from learning_assistant.rag.indexing.metadata_builder import MetadataBuilder
from learning_assistant.rag.vectorstores.base import VectorStore


class DocumentIndexer:
    """Indexes documents into a vector store."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        chunk_processor: ChunkProcessor | None = None,
        metadata_builder: MetadataBuilder | None = None,
    ) -> None:
        self._embedding = embedding_provider
        self._store = vector_store
        self._chunker = chunk_processor or ChunkProcessor()
        self._meta = metadata_builder or MetadataBuilder()

    async def index_document(
        self, document: PDFDocument, text: str
    ) -> int:
        chunks = self._chunker.process(text, document.id)
        return await self._index_chunks(chunks, document.filename)

    async def index_text(
        self, text: str, source: str = "", filename: str = ""
    ) -> int:
        chunks = self._chunker.process(text)
        return await self._index_chunks(chunks, filename or source)

    async def _index_chunks(
        self, chunks: list[DocumentChunk], filename: str
    ) -> int:
        if not chunks:
            return 0
        texts = [c.content for c in chunks]
        embeddings = await self._embedding.embed_documents(texts)
        metadata_list = self._meta.build_batch(chunks, filename=filename)
        retrieved = [
            RetrievedChunk(
                content=c.content,
                score=1.0,
                metadata=m,
                chunk_id=c.id,
                source=filename,
                page=c.page_number,
            )
            for c, m in zip(chunks, metadata_list, strict=True)
        ]
        await self._store.add_documents(retrieved, embeddings)
        return len(chunks)
