"""Tests for MCPResourceAdapter."""

from learning_assistant.mcp.adapters.resource_adapter import MCPResourceAdapter
from learning_assistant.models.document import PDFDocument


class TestMCPResourceAdapter:
    def test_from_document(self) -> None:
        doc = PDFDocument(
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size=100,
            page_count=1,
            content_hash="abc",
        )
        resource = MCPResourceAdapter.from_document(doc, content="text")
        assert resource.name == "test.pdf"
        assert resource.content == "text"
        assert resource.mime_type == "application/pdf"
        assert "test.pdf" in resource.uri

    def test_from_text(self) -> None:
        resource = MCPResourceAdapter.from_text("hello", name="test")
        assert resource.name == "test"
        assert resource.content == "hello"
        assert resource.uri == "text://test"

    def test_from_text_custom_uri(self) -> None:
        resource = MCPResourceAdapter.from_text("hello", name="test", uri="custom://uri")
        assert resource.uri == "custom://uri"
