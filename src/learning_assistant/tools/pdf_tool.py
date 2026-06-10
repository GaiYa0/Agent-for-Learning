"""PDF reading tool — wraps PDFService."""

from learning_assistant.models.tool import ToolResult
from learning_assistant.services.pdf.pdf_service import PDFService
from learning_assistant.tools.base import BaseTool, ParameterSpec
from learning_assistant.tools.exceptions import ToolExecutionError


class PDFTool(BaseTool):
    """Reads and extracts text from PDF files."""

    def __init__(self, pdf_service: PDFService | None = None) -> None:
        self._pdf_service = pdf_service or PDFService()

    @property
    def name(self) -> str:
        return "pdf_reader"

    @property
    def description(self) -> str:
        return "Read a PDF file and extract its text content"

    @property
    def category(self) -> str:
        return "pdf"

    @property
    def parameters(self) -> dict[str, ParameterSpec]:
        return {
            "file_path": ParameterSpec(
                type="string",
                description="Absolute path to the PDF file",
                required=True,
            ),
        }

    async def execute(self, **kwargs: str) -> ToolResult:
        file_path = kwargs["file_path"]
        try:
            doc, text = await self._pdf_service.load_with_text(file_path)
        except Exception as e:
            raise ToolExecutionError(f"PDF read failed: {e}") from e
        return ToolResult(
            tool_call_id="",
            success=True,
            content=f"Document: {doc.filename} ({doc.page_count} pages)\n\n{text}",
        )
