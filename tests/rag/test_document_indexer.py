"""Tests for DocumentIndexer — offline only."""

import pytest

from learning_assistant.models.document import PDFDocument
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.indexing.document_indexer import DocumentIndexer
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


@pytest.fixture()
def indexer() -> DocumentIndexer:
    return DocumentIndexer(
        embedding_provider=MockEmbeddingProvider(dim=64),
        vector_store=InMemoryVectorStore(),
    )


@pytest.fixture()
def document() -> PDFDocument:
    return PDFDocument(
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        file_size=1000,
        page_count=1,
        content_hash="abc123",
    )


class TestDocumentIndexer:
    @pytest.mark.asyncio
    async def test_index_document(
        self, indexer: DocumentIndexer, document: PDFDocument
    ) -> None:
        count = await indexer.index_document(document, "Hello world. " * 200)
        assert count > 0
        assert await indexer._store.count() > 0

    @pytest.mark.asyncio
    async def test_index_text(self, indexer: DocumentIndexer) -> None:
        count = await indexer.index_text("Test content. " * 200, source="manual")
        assert count > 0

    @pytest.mark.asyncio
    async def test_index_empty_text(
        self, indexer: DocumentIndexer, document: PDFDocument
    ) -> None:
        count = await indexer.index_document(document, "")
        assert count == 0

    @pytest.mark.asyncio
    async def test_index_short_text(
        self, indexer: DocumentIndexer, document: PDFDocument
    ) -> None:
        count = await indexer.index_document(document, "Short text.")
        assert count == 1
