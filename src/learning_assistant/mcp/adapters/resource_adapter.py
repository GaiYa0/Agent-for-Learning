"""Resource adapter — bridges local documents to MCP resource format."""

from learning_assistant.mcp.client.base import MCPResource
from learning_assistant.models.document import PDFDocument


class MCPResourceAdapter:
    """Adapts local documents to MCP protocol format."""

    @staticmethod
    def from_document(doc: PDFDocument, content: str = "") -> MCPResource:
        return MCPResource(
            uri=f"file://{doc.file_path}",
            name=doc.filename,
            content=content,
            mime_type="application/pdf",
        )

    @staticmethod
    def from_text(text: str, name: str, uri: str = "") -> MCPResource:
        return MCPResource(
            uri=uri or f"text://{name}",
            name=name,
            content=text,
        )
