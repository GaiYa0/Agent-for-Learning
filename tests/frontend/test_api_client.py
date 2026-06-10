"""Tests for APIClient — offline, no real HTTP."""

import inspect
import json
from unittest.mock import MagicMock, patch

from learning_assistant.frontend.services.api_client import APIClient


class TestAPIClientInit:
    def test_default_url(self) -> None:
        client = APIClient()
        assert client.base_url == "http://localhost:8000"

    def test_custom_url(self) -> None:
        client = APIClient(base_url="http://custom:9000")
        assert client.base_url == "http://custom:9000"


class TestAPIClientMethods:
    def test_has_chat(self) -> None:
        client = APIClient()
        assert callable(getattr(client, "chat", None))

    def test_has_chat_stream(self) -> None:
        client = APIClient()
        assert callable(getattr(client, "chat_stream", None))

    def test_has_rag_chat(self) -> None:
        client = APIClient()
        assert callable(getattr(client, "rag_chat", None))

    def test_has_upload(self) -> None:
        client = APIClient()
        assert callable(getattr(client, "upload", None))

    def test_has_search(self) -> None:
        client = APIClient()
        assert callable(getattr(client, "search", None))

    def test_has_health(self) -> None:
        client = APIClient()
        assert callable(getattr(client, "health", None))


class TestAPIClientChatStream:
    @patch("learning_assistant.frontend.services.api_client.httpx.Client")
    def test_chat_stream_returns_iterable_generator(
        self, mock_client_cls: MagicMock
    ) -> None:
        client = APIClient()
        sse_lines = [
            f'data: {json.dumps({"type": "token", "content": "Hi"})}',
            f'data: {json.dumps({"type": "done", "answer": "Hi"})}',
        ]

        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(sse_lines)
        mock_response.raise_for_status = MagicMock()

        mock_stream_ctx = MagicMock()
        mock_stream_ctx.__enter__.return_value = mock_response
        mock_stream_ctx.__exit__.return_value = False

        mock_http = MagicMock()
        mock_http.stream.return_value = mock_stream_ctx

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_http
        mock_client.__exit__.return_value = False
        mock_client_cls.return_value = mock_client

        stream = client.chat_stream("s1", "hello")

        assert inspect.isgenerator(stream)
        tokens = list(stream)
        assert tokens == ["Hi"]
        assert client.last_stream_meta.get("answer") == "Hi"
