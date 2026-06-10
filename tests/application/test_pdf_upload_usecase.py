"""Tests for PDFUploadUseCase."""

import pytest

from learning_assistant.application.dto.upload_request import UploadRequest
from learning_assistant.application.orchestrators.rag_orchestrator import RAGOrchestrator
from learning_assistant.application.usecases.pdf_upload_usecase import PDFUploadUseCase
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.pipelines.retrieval_pipeline import RetrievalPipeline
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


@pytest.fixture()
def usecase() -> PDFUploadUseCase:
    emb = MockEmbeddingProvider(dim=64)
    store = InMemoryVectorStore()
    retriever = SimilarityRetriever(emb, store)
    pipeline = RetrievalPipeline(retriever)
    rag_orch = RAGOrchestrator(emb, store, pipeline)
    return PDFUploadUseCase(rag_orch)


class TestPDFUploadUseCase:
    @pytest.mark.asyncio
    async def test_upload_success(
        self, usecase: PDFUploadUseCase, tmp_path
    ) -> None:
        f = tmp_path / "test.txt"
        f.write_text("Hello world. " * 200)
        req = UploadRequest(file_path=str(f))
        result = await usecase.execute(req)
        assert result.success is True
        assert result.data.chunks_indexed > 0
        assert result.data.filename == "test.txt"

    @pytest.mark.asyncio
    async def test_upload_nonexistent(
        self, usecase: PDFUploadUseCase
    ) -> None:
        req = UploadRequest(file_path="/nonexistent/file.txt")
        result = await usecase.execute(req)
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_upload_empty_file(
        self, usecase: PDFUploadUseCase, tmp_path
    ) -> None:
        f = tmp_path / "empty.txt"
        f.write_text("")
        req = UploadRequest(file_path=str(f))
        result = await usecase.execute(req)
        assert result.success is False
        assert "empty" in result.error.lower()
