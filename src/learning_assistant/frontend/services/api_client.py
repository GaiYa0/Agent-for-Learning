"""API client — communicates with the FastAPI backend."""

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class APIClient:
    """HTTP client for the Learning Assistant API."""

    base_url: str = "http://localhost:8000"
    timeout: float = 30.0
    api_key: str = ""
    last_stream_meta: dict[str, Any] = field(default_factory=dict)

    async def chat(
        self, session_id: str, message: str, use_rag: bool = False
    ) -> dict[str, Any]:
        return await self._post(
            "/chat",
            {"session_id": session_id, "message": message, "use_rag": use_rag},
        )

    async def rag_chat(
        self, session_id: str, message: str, top_k: int = 5
    ) -> dict[str, Any]:
        return await self._post(
            "/rag/chat",
            {"session_id": session_id, "message": message, "top_k": top_k},
        )

    def chat_stream(
        self,
        session_id: str,
        message: str,
        *,
        use_rag: bool = False,
        top_k: int = 5,
    ) -> Iterator[str]:
        """Stream token chunks from the SSE chat endpoint."""
        if use_rag:
            path = "/rag/chat/stream"
            payload: dict[str, Any] = {
                "session_id": session_id,
                "message": message,
                "top_k": top_k,
            }
        else:
            path = "/chat/stream"
            payload = {
                "session_id": session_id,
                "message": message,
                "use_rag": False,
            }

        self.last_stream_meta = {}
        with httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._headers(),
        ) as client:
            with client.stream("POST", path, json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    data: dict[str, Any] = json.loads(line[6:])
                    event_type = data.get("type")
                    if event_type == "token":
                        content = data.get("content", "")
                        if content:
                            yield str(content)
                    elif event_type == "done":
                        self.last_stream_meta = data
                    elif event_type == "error":
                        message_text = data.get("message", "Stream error")
                        raise RuntimeError(str(message_text))

    async def upload(self, filename: str, content: bytes) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, headers=self._headers()
        ) as c:
            resp = await c.post(
                "/documents/upload",
                files={"file": (filename, content, "application/octet-stream")},
            )
            resp.raise_for_status()
            result: dict[str, Any] = resp.json()
            return result

    async def search(self, query: str, max_results: int = 5) -> dict[str, Any]:
        return await self._post(
            "/search", {"query": query, "max_results": max_results}
        )

    async def health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, headers=self._headers()
        ) as c:
            resp = await c.get("/health")
            resp.raise_for_status()
            result: dict[str, Any] = resp.json()
            return result

    def _headers(self) -> dict[str, str]:
        if self.api_key:
            return {"X-API-Key": self.api_key}
        return {}

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, headers=self._headers()
        ) as c:
            resp = await c.post(path, json=payload)
            resp.raise_for_status()
            result: dict[str, Any] = resp.json()
            return result
