"""API key authentication."""

from fastapi import Security
from fastapi.security import APIKeyHeader

from learning_assistant.api.exceptions import UnauthorizedError

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_configured_keys: set[str] = set()


def configure_api_keys(keys: set[str]) -> None:
    global _configured_keys
    _configured_keys = keys


async def verify_api_key(
    api_key: str | None = Security(_api_key_header),
) -> str:
    if not _configured_keys:
        return "no-auth"
    if api_key is None:
        raise UnauthorizedError("Missing API key")
    if api_key not in _configured_keys:
        raise UnauthorizedError("Invalid API key")
    return api_key
