"""Tests for streaming chat API endpoints."""

import json

from fastapi.testclient import TestClient


class TestChatStreamAPI:
    def test_chat_stream_emits_tokens_and_done(self, client: TestClient) -> None:
        response = client.post(
            "/chat/stream",
            json={"session_id": "s1", "message": "Hello"},
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        events = []
        for line in response.text.splitlines():
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))

        assert any(e["type"] == "token" for e in events)
        done = next(e for e in events if e["type"] == "done")
        assert "answer" in done
        assert done["answer"]

    def test_rag_chat_stream_emits_done(self, client: TestClient) -> None:
        response = client.post(
            "/rag/chat/stream",
            json={"session_id": "s1", "message": "Hello", "top_k": 3},
        )
        assert response.status_code == 200

        events = []
        for line in response.text.splitlines():
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))

        done = next(e for e in events if e["type"] == "done")
        assert done["answer"]

    def test_chat_stream_rejects_empty_message(self, client: TestClient) -> None:
        response = client.post(
            "/chat/stream",
            json={"session_id": "s1", "message": "   "},
        )
        assert response.status_code == 200
        events = []
        for line in response.text.splitlines():
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))
        assert events
        assert events[0]["type"] == "error"
