"""PDF document reading and text extraction."""

import hashlib
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError as PyPdfReadError

from learning_assistant.models.document import PDFDocument
from learning_assistant.services.base import BaseService
from learning_assistant.services.exceptions import PDFEmptyError, PDFReadError


class PDFService(BaseService):
    """Reads PDF files and produces PDFDocument models."""

    @property
    def service_name(self) -> str:
        return "pdf"

    async def health_check(self) -> bool:
        return True

    async def close(self) -> None:
        pass

    async def load_document(self, file_path: str | Path) -> PDFDocument:
        path = Path(file_path)
        self._validate_path(path)
        reader, data = self._read_pdf(path)
        page_count = len(reader.pages)
        if page_count == 0:
            raise PDFEmptyError(f"PDF has no pages: {path}")
        text = self._extract_all_text(reader)
        if not text.strip():
            raise PDFEmptyError(f"PDF has no extractable text: {path}")
        return PDFDocument(
            filename=path.name,
            file_path=str(path.resolve()),
            file_size=len(data),
            page_count=page_count,
            title=reader.metadata.title if reader.metadata else None,
            author=reader.metadata.author if reader.metadata else None,
            content_hash=hashlib.sha256(data).hexdigest(),
        )

    async def load_with_text(
        self, file_path: str | Path
    ) -> tuple[PDFDocument, str]:
        """Load metadata and full text in a single disk read."""
        path = Path(file_path)
        self._validate_path(path)
        reader, data = self._read_pdf(path)
        page_count = len(reader.pages)
        if page_count == 0:
            raise PDFEmptyError(f"PDF has no pages: {path}")
        text = self._extract_all_text(reader)
        if not text.strip():
            raise PDFEmptyError(f"PDF has no extractable text: {path}")
        doc = PDFDocument(
            filename=path.name,
            file_path=str(path.resolve()),
            file_size=len(data),
            page_count=page_count,
            title=reader.metadata.title if reader.metadata else None,
            author=reader.metadata.author if reader.metadata else None,
            content_hash=hashlib.sha256(data).hexdigest(),
        )
        return doc, text

    async def extract_text(self, file_path: str | Path) -> str:
        path = Path(file_path)
        self._validate_path(path)
        reader, _ = self._read_pdf(path)
        return self._extract_all_text(reader)

    async def extract_pages(
        self, file_path: str | Path, pages: list[int] | None = None
    ) -> dict[int, str]:
        path = Path(file_path)
        self._validate_path(path)
        reader, _ = self._read_pdf(path)
        target_pages = pages if pages is not None else list(range(len(reader.pages)))
        result: dict[int, str] = {}
        for idx in target_pages:
            if 0 <= idx < len(reader.pages):
                result[idx] = reader.pages[idx].extract_text() or ""
        return result

    async def get_metadata(self, file_path: str | Path) -> dict[str, str]:
        path = Path(file_path)
        self._validate_path(path)
        reader, _ = self._read_pdf(path)
        meta = reader.metadata
        if meta is None:
            return {}
        return {
            k: str(v)
            for k, v in {
                "title": meta.title,
                "author": meta.author,
                "subject": meta.subject,
                "creator": meta.creator,
            }.items()
            if v is not None
        }

    def _validate_path(self, path: Path) -> None:
        if not path.exists():
            raise PDFReadError(f"File not found: {path}")
        if not path.is_file():
            raise PDFReadError(f"Not a file: {path}")
        if path.suffix.lower() != ".pdf":
            raise PDFReadError(f"Not a PDF file: {path}")

    def _read_pdf(self, path: Path) -> tuple[PdfReader, bytes]:
        try:
            data = path.read_bytes()
            reader = PdfReader(BytesIO(data))
        except OSError as e:
            raise PDFReadError(f"Cannot read PDF: {path}") from e
        except PyPdfReadError as e:
            raise PDFReadError(f"Corrupted PDF: {path}") from e
        return reader, data

    def _extract_all_text(self, reader: PdfReader) -> str:
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
        return "\n\n".join(parts)
