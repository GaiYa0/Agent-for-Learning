"""Tests for RAG API endpoint."""

from fastapi.testclient import TestClient


def test_rag_chat(client: TestClient) -> None:
    resp = client.post(
        "/rag/chat",
        json={"session_id": "s1", "message": "What is Python?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "answer" in body["data"]
