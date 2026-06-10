"""Tests for upload API endpoint."""

from fastapi.testclient import TestClient


def test_upload(client: TestClient) -> None:
    resp = client.post(
        "/documents/upload",
        files={"file": ("test.txt", b"Hello world content here.", "text/plain")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["filename"] == "test.txt"
