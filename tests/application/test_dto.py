"""Tests for DTO models."""

from learning_assistant.application.dto.chat_request import ChatRequest
from learning_assistant.application.dto.chat_response import ChatResponse
from learning_assistant.application.dto.common import Result
from learning_assistant.application.dto.search_request import SearchRequest, SearchResponseDTO
from learning_assistant.application.dto.upload_request import IndexResult, UploadRequest


class TestResult:
    def test_ok(self) -> None:
        r = Result.ok("data")
        assert r.success is True
        assert r.data == "data"
        assert r.error is None

    def test_fail(self) -> None:
        r = Result.fail("error msg")
        assert r.success is False
        assert r.data is None
        assert r.error == "error msg"


class TestChatRequest:
    def test_create(self) -> None:
        r = ChatRequest(session_id="s1", message="hi")
        assert r.use_rag is False

    def test_with_rag(self) -> None:
        r = ChatRequest(session_id="s1", message="hi", use_rag=True)
        assert r.use_rag is True


class TestChatResponse:
    def test_create(self) -> None:
        r = ChatResponse(answer="hello")
        assert r.citations == []
        assert r.metadata.iterations == 0


class TestUploadRequest:
    def test_create(self) -> None:
        r = UploadRequest(file_path="/tmp/f.txt")
        assert r.source == ""


class TestIndexResult:
    def test_create(self) -> None:
        r = IndexResult(filename="f.txt", chunks_indexed=5)
        assert r.document_id == ""


class TestSearchRequest:
    def test_create(self) -> None:
        r = SearchRequest(query="Python")
        assert r.max_results == 5


class TestSearchResponseDTO:
    def test_create(self) -> None:
        r = SearchResponseDTO(query="q", results=[], provider="mock")
        assert r.provider == "mock"
