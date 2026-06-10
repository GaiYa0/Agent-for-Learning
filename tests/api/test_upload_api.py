"""Tests for upload API endpoint."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from learning_assistant.api.routers.upload import resolve_upload_suffix
from learning_assistant.models.document import PDFDocument
from learning_assistant.services.pdf.pdf_service import PDFService


def test_resolve_upload_suffix_from_filename() -> None:
    assert resolve_upload_suffix("lecture.pdf", b"content") == ".pdf"
    assert resolve_upload_suffix("notes.txt", b"content") == ".txt"


def test_resolve_upload_suffix_from_pdf_magic_bytes() -> None:
    assert resolve_upload_suffix("upload.bin", b"%PDF-1.4 data") == ".pdf"


def test_resolve_upload_suffix_defaults_to_txt() -> None:
    assert resolve_upload_suffix("data.csv", b"hello") == ".txt"


def test_upload(client: TestClient) -> None:
    resp = client.post(
        "/documents/upload",
        files={"file": ("test.txt", b"Hello world content here.", "text/plain")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["filename"] == "test.txt"


def test_upload_pdf_uses_pdf_parser(client: TestClient) -> None:
    pdf_bytes = b"%PDF-1.4 mock"
    document = PDFDocument(
        filename="lecture.pdf",
        file_path="/tmp/lecture.pdf",
        file_size=len(pdf_bytes),
        page_count=1,
        content_hash="deadbeef",
    )

    async def fake_load_with_text(path: Path) -> tuple[PDFDocument, str]:
        assert path.suffix.lower() == ".pdf"
        return document, "Deadlock occurs when processes wait for each other."

    with patch.object(
        PDFService,
        "load_with_text",
        new=AsyncMock(side_effect=fake_load_with_text),
    ):
        resp = client.post(
            "/documents/upload",
            files={"file": ("lecture.pdf", pdf_bytes, "application/pdf")},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["filename"] == "lecture.pdf"
    assert body["data"]["chunks_indexed"] > 0


def test_upload_pdf_rejects_unreadable_text(client: TestClient) -> None:
    from learning_assistant.services.exceptions import PDFUnreadableTextError

    async def fake_load_with_text(path: Path) -> tuple[PDFDocument, str]:
        raise PDFUnreadableTextError(
            "PDF text appears unreadable; it may be scanned or corrupted. "
            "Please upload a PDF with selectable text."
        )

    with patch.object(
        PDFService,
        "load_with_text",
        new=AsyncMock(side_effect=fake_load_with_text),
    ):
        resp = client.post(
            "/documents/upload",
            files={"file": ("bad.pdf", b"%PDF-1.4", "application/pdf")},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "unreadable" in body["error"].lower()
