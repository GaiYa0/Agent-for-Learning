"""Tests for exception middleware."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from learning_assistant.api.middleware.exception import ExceptionMiddleware
from learning_assistant.api.middleware.request_id import RequestIdMiddleware


def test_unhandled_error_returns_json() -> None:
    app = FastAPI()
    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(RequestIdMiddleware)

    @app.get("/crash")
    async def crash() -> None:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/crash")
    assert resp.status_code == 500
    body = resp.json()
    assert body["success"] is False
    assert "boom" in body["error"]["message"]
