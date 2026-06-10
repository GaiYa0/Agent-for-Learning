"""Tests for chat API endpoint."""

from fastapi.testclient import TestClient


def test_chat(client: TestClient) -> None:
    resp = client.post(
        "/chat",
        json={"session_id": "s1", "message": "What is 6x7?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "answer" in body["data"]


def test_chat_with_rag(client: TestClient) -> None:
    resp = client.post(
        "/chat",
        json={"session_id": "s1", "message": "Hello", "use_rag": True},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True


def test_chat_empty_message(client: TestClient) -> None:
    resp = client.post("/chat", json={"session_id": "s1", "message": ""})
    assert resp.status_code == 422
