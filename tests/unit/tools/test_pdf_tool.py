"""Tests for PDFTool."""

from unittest.mock import AsyncMock

import pytest

from learning_assistant.models.document import PDFDocument
from learning_assistant.tools.exceptions import ToolExecutionError
from learning_assistant.tools.pdf_tool import PDFTool


def _mock_pdf_service(
    text: str = "Hello", page_count: int = 1, filename: str = "test.pdf"
):
    svc = AsyncMock()
    doc = PDFDocument(
        filename=filename,
        file_path="/tmp/test.pdf",
        file_size=100,
        page_count=page_count,
        content_hash="abc",
    )
    svc.load_with_text.return_value = (doc, text)
    return svc


@pytest.fixture()
def tool() -> PDFTool:
    return PDFTool(pdf_service=_mock_pdf_service())


class TestPDFTool:
    def test_name(self, tool: PDFTool) -> None:
        assert tool.name == "pdf_reader"

    def test_category(self, tool: PDFTool) -> None:
        assert tool.category == "pdf"

    def test_schema(self, tool: PDFTool) -> None:
        s = tool.schema()
        assert s["name"] == "pdf_reader"
        assert "file_path" in s["parameters"]["properties"]

    @pytest.mark.asyncio
    async def test_execute_success(self, tool: PDFTool) -> None:
        result = await tool.execute(file_path="/tmp/test.pdf")
        assert result.is_success()
        assert "Hello" in result.content

    @pytest.mark.asyncio
    async def test_execute_service_error(self) -> None:
        svc = AsyncMock()
        svc.load_with_text.side_effect = FileNotFoundError("not found")
        t = PDFTool(pdf_service=svc)
        with pytest.raises(ToolExecutionError, match="PDF read failed"):
            await t.execute(file_path="/tmp/bad.pdf")
