"""Tests for API key authentication."""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from learning_assistant.api.security.api_key import configure_api_keys, verify_api_key


def _app_with_auth() -> FastAPI:
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(verify_api_key)])
    async def protected() -> dict:
        return {"ok": True}

    return app


def test_no_keys_allows_all() -> None:
    configure_api_keys(set())
    client = TestClient(_app_with_auth())
    resp = client.get("/protected")
    assert resp.status_code == 200


def test_valid_key() -> None:
    configure_api_keys({"test-key-123"})
    client = TestClient(_app_with_auth())
    resp = client.get("/protected", headers={"X-API-Key": "test-key-123"})
    assert resp.status_code == 200


def test_invalid_key() -> None:
    configure_api_keys({"test-key-123"})
    client = TestClient(_app_with_auth())
    resp = client.get("/protected", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401


def test_missing_key() -> None:
    configure_api_keys({"test-key-123"})
    client = TestClient(_app_with_auth())
    resp = client.get("/protected")
    assert resp.status_code == 401
