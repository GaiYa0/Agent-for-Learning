"""Tests for PDFService."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from learning_assistant.services.exceptions import PDFEmptyError, PDFReadError
from learning_assistant.services.pdf.pdf_service import PDFService


@pytest.fixture()
def pdf_service() -> PDFService:
    return PDFService()


class TestPDFServiceMetadata:
    @pytest.mark.asyncio
    async def test_service_name(self, pdf_service: PDFService) -> None:
        assert pdf_service.service_name == "pdf"

    @pytest.mark.asyncio
    async def test_health_check(self, pdf_service: PDFService) -> None:
        assert await pdf_service.health_check() is True

    @pytest.mark.asyncio
    async def test_close(self, pdf_service: PDFService) -> None:
        await pdf_service.close()  # should not raise


class TestPDFServiceValidation:
    @pytest.mark.asyncio
    async def test_nonexistent_file_raises(self, pdf_service: PDFService) -> None:
        with pytest.raises(PDFReadError, match="File not found"):
            await pdf_service.load_document("/nonexistent/file.pdf")

    @pytest.mark.asyncio
    async def test_non_pdf_extension_raises(
        self, pdf_service: PDFService, tmp_path: Path
    ) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello")
        with pytest.raises(PDFReadError, match="Not a PDF"):
            await pdf_service.load_document(str(f))

    @pytest.mark.asyncio
    async def test_extract_text_nonexistent_raises(
        self, pdf_service: PDFService
    ) -> None:
        with pytest.raises(PDFReadError, match="File not found"):
            await pdf_service.extract_text("/nonexistent.pdf")

    @pytest.mark.asyncio
    async def test_extract_pages_nonexistent_raises(
        self, pdf_service: PDFService
    ) -> None:
        with pytest.raises(PDFReadError, match="File not found"):
            await pdf_service.extract_pages("/nonexistent.pdf")

    @pytest.mark.asyncio
    async def test_get_metadata_nonexistent_raises(
        self, pdf_service: PDFService
    ) -> None:
        with pytest.raises(PDFReadError, match="File not found"):
            await pdf_service.get_metadata("/nonexistent.pdf")


class TestPDFServiceLoadDocument:
    @pytest.mark.asyncio
    async def test_load_valid_pdf(
        self, pdf_service: PDFService, tmp_path: Path
    ) -> None:
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 minimal")
        with patch.object(
            pdf_service, "_read_pdf"
        ) as mock_reader, patch.object(
            pdf_service, "_validate_path"
        ), patch.object(
            pdf_service, "_extract_all_text", return_value="Hello world"
        ):
            reader = MagicMock()
            reader.pages = [MagicMock()]
            reader.metadata = None
            mock_reader.return_value = (reader, b"%PDF-1.4 minimal")
            with (
                patch.object(Path, "stat", return_value=MagicMock(st_size=100)),
                patch.object(Path, "read_bytes", return_value=b"%PDF-1.4 minimal"),
            ):
                doc = await pdf_service.load_document(pdf_path)
        assert doc.filename == "test.pdf"
        assert doc.page_count == 1

    @pytest.mark.asyncio
    async def test_empty_pdf_raises(
        self, pdf_service: PDFService, tmp_path: Path
    ) -> None:
        pdf_path = tmp_path / "empty.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        with patch.object(
            pdf_service, "_validate_path"
        ), patch.object(
            pdf_service, "_read_pdf"
        ) as mock_reader:
            reader = MagicMock()
            reader.pages = []
            mock_reader.return_value = (reader, b"%PDF-1.4 minimal")
            with pytest.raises(PDFEmptyError, match="no pages"):
                await pdf_service.load_document(pdf_path)

    @pytest.mark.asyncio
    async def test_no_text_pdf_raises(
        self, pdf_service: PDFService, tmp_path: Path
    ) -> None:
        pdf_path = tmp_path / "blank.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        with patch.object(
            pdf_service, "_validate_path"
        ), patch.object(
            pdf_service, "_read_pdf"
        ) as mock_reader, patch.object(
            pdf_service, "_extract_all_text", return_value=""
        ):
            reader = MagicMock()
            reader.pages = [MagicMock()]
            mock_reader.return_value = (reader, b"%PDF-1.4 minimal")
            with pytest.raises(PDFEmptyError, match="no extractable text"):
                await pdf_service.load_document(pdf_path)


class TestPDFServiceExtractText:
    @pytest.mark.asyncio
    async def test_extract_text_success(
        self, pdf_service: PDFService, tmp_path: Path
    ) -> None:
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        with patch.object(
            pdf_service, "_validate_path"
        ), patch.object(
            pdf_service, "_read_pdf"
        ) as mock_reader:
            page = MagicMock()
            page.extract_text.return_value = "Page text"
            reader = MagicMock()
            reader.pages = [page]
            mock_reader.return_value = (reader, b"%PDF-1.4 minimal")
            result = await pdf_service.extract_text(pdf_path)
        assert result == "Page text"


class TestPDFServiceExtractPages:
    @pytest.mark.asyncio
    async def test_extract_specific_pages(
        self, pdf_service: PDFService, tmp_path: Path
    ) -> None:
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        with patch.object(
            pdf_service, "_validate_path"
        ), patch.object(
            pdf_service, "_read_pdf"
        ) as mock_reader:
            p0 = MagicMock()
            p0.extract_text.return_value = "Page 0"
            p1 = MagicMock()
            p1.extract_text.return_value = "Page 1"
            reader = MagicMock()
            reader.pages = [p0, p1]
            mock_reader.return_value = (reader, b"%PDF-1.4 minimal")
            result = await pdf_service.extract_pages(pdf_path, [0])
        assert 0 in result
        assert 1 not in result

    @pytest.mark.asyncio
    async def test_extract_all_pages(
        self, pdf_service: PDFService, tmp_path: Path
    ) -> None:
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        with patch.object(
            pdf_service, "_validate_path"
        ), patch.object(
            pdf_service, "_read_pdf"
        ) as mock_reader:
            p0 = MagicMock()
            p0.extract_text.return_value = "Page 0"
            reader = MagicMock()
            reader.pages = [p0]
            mock_reader.return_value = (reader, b"%PDF-1.4 minimal")
            result = await pdf_service.extract_pages(pdf_path)
        assert 0 in result


class TestPDFServiceGetMetadata:
    @pytest.mark.asyncio
    async def test_metadata_with_info(
        self, pdf_service: PDFService, tmp_path: Path
    ) -> None:
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        with patch.object(
            pdf_service, "_validate_path"
        ), patch.object(
            pdf_service, "_read_pdf"
        ) as mock_reader:
            meta = MagicMock()
            meta.title = "My Book"
            meta.author = "Author"
            meta.subject = None
            meta.creator = "Writer"
            reader = MagicMock()
            reader.metadata = meta
            mock_reader.return_value = (reader, b"%PDF-1.4 minimal")
            result = await pdf_service.get_metadata(pdf_path)
        assert result["title"] == "My Book"
        assert "subject" not in result

    @pytest.mark.asyncio
    async def test_metadata_none(
        self, pdf_service: PDFService, tmp_path: Path
    ) -> None:
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        with patch.object(
            pdf_service, "_validate_path"
        ), patch.object(
            pdf_service, "_read_pdf"
        ) as mock_reader:
            reader = MagicMock()
            reader.metadata = None
            mock_reader.return_value = (reader, b"%PDF-1.4 minimal")
            result = await pdf_service.get_metadata(pdf_path)
        assert result == {}


class TestPDFServiceReadableText:
    def test_validate_readable_text_accepts_normal_text(
        self, pdf_service: PDFService
    ) -> None:
        pdf_service._validate_readable_text(
            "Deadlock is a classic operating systems topic.\n"
        )

    def test_validate_readable_text_rejects_gibberish(
        self, pdf_service: PDFService
    ) -> None:
        from learning_assistant.services.exceptions import PDFUnreadableTextError

        gibberish = "\x00\x01\x02" * 100 + "abc"
        with pytest.raises(PDFUnreadableTextError, match="unreadable"):
            pdf_service._validate_readable_text(gibberish)
