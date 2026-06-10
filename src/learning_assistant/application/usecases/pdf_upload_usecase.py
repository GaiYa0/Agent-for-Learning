"""PDF upload use case — indexes a document into the vector store."""

from pathlib import Path

from learning_assistant.application.dto.common import Result
from learning_assistant.application.dto.upload_request import IndexResult, UploadRequest
from learning_assistant.application.orchestrators.rag_orchestrator import RAGOrchestrator
from learning_assistant.application.usecases.base import BaseUseCase
from learning_assistant.services.pdf.pdf_service import PDFService


class PDFUploadUseCase(BaseUseCase[UploadRequest, IndexResult]):
    """Indexes a text/PDF file into the vector store."""

    def __init__(
        self,
        rag_orchestrator: RAGOrchestrator,
        pdf_service: PDFService | None = None,
    ) -> None:
        self._rag = rag_orchestrator
        self._pdf = pdf_service or PDFService()

    async def execute(self, input_dto: UploadRequest) -> Result[IndexResult]:
        try:
            path = Path(input_dto.file_path)
            if not path.exists():
                return Result.fail(f"File not found: {input_dto.file_path}")

            if path.suffix.lower() == ".pdf":
                document, text = await self._pdf.load_with_text(path)
                chunks = await self._rag.get_indexer().index_document(document, text)
                return Result.ok(
                    IndexResult(
                        filename=document.filename,
                        chunks_indexed=chunks,
                        document_id=document.id,
                    )
                )

            text = path.read_text(encoding="utf-8", errors="ignore")
            if not text.strip():
                return Result.fail("File is empty")
            chunks = await self._rag.index_text(
                text, source=input_dto.source or path.name
            )
            return Result.ok(
                IndexResult(
                    filename=path.name,
                    chunks_indexed=chunks,
                    document_id="",
                )
            )
        except Exception as e:
            return Result.fail(str(e))
