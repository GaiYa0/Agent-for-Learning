"""Tests for search API endpoint."""

from fastapi.testclient import TestClient


def test_search(client: TestClient) -> None:
    resp = client.post("/search", json={"query": "Python tutorials"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["query"] == "Python tutorials"


def test_search_empty_query(client: TestClient) -> None:
    resp = client.post("/search", json={"query": ""})
    assert resp.status_code == 422
