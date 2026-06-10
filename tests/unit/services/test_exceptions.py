"""Tests for service exception hierarchy."""

from learning_assistant.services.exceptions import (
    ChunkError,
    PDFEmptyError,
    PDFError,
    PDFReadError,
    ProviderError,
    SearchError,
    ServiceError,
)


class TestExceptionHierarchy:
    def test_service_error_is_base(self) -> None:
        assert issubclass(ServiceError, Exception)

    def test_pdf_errors_inherit_correctly(self) -> None:
        assert issubclass(PDFError, ServiceError)
        assert issubclass(PDFReadError, PDFError)
        assert issubclass(PDFEmptyError, PDFError)

    def test_search_errors_inherit_correctly(self) -> None:
        assert issubclass(SearchError, ServiceError)
        assert issubclass(ProviderError, SearchError)

    def test_chunk_error_inherits_service_error(self) -> None:
        assert issubclass(ChunkError, ServiceError)

    def test_exceptions_carry_message(self) -> None:
        assert str(ServiceError("msg")).endswith("msg")
        assert str(PDFReadError("bad file")).endswith("bad file")
        assert str(ProviderError("timeout")).endswith("timeout")
