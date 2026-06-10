"""Tests for ResponseBuilder."""

from learning_assistant.api.responses.response_builder import ResponseBuilder


class TestResponseBuilder:
    def test_success(self) -> None:
        resp = ResponseBuilder.success(data="hello", request_id="r1")
        assert resp.success is True
        assert resp.data == "hello"
        assert resp.request_id == "r1"
        assert resp.error is None

    def test_error(self) -> None:
        resp = ResponseBuilder.error(message="oops", code="ERR", request_id="r1")
        assert resp.success is False
        assert resp.error.code == "ERR"
        assert resp.error.message == "oops"
        assert resp.request_id == "r1"
