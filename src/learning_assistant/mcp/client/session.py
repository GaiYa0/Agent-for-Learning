"""MCP session — manages connection lifecycle with retry and heartbeat."""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any, TypeVar

from learning_assistant.mcp.exceptions import MCPConnectionError, MCPTimeoutError

T = TypeVar("T")
CoroFactory = Callable[[], Coroutine[Any, Any, Any]]

logger = logging.getLogger(__name__)


@dataclass
class SessionConfig:
    timeout: float = 30.0
    max_retries: int = 3
    heartbeat_interval: float = 60.0


class MCPSession:
    """Manages an MCP client session with retry and heartbeat."""

    def __init__(self, config: SessionConfig | None = None) -> None:
        self._config = config or SessionConfig()
        self._connected: bool = False
        self._retry_count: int = 0

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        self._connected = True
        self._retry_count = 0
        logger.info("MCP session connected")

    async def disconnect(self) -> None:
        self._connected = False
        logger.info("MCP session disconnected")

    async def execute_with_retry(self, operation: str, coro_factory: CoroFactory) -> Any:
        last_error: Exception | None = None
        for attempt in range(self._config.max_retries):
            try:
                return await asyncio.wait_for(
                    coro_factory(), timeout=self._config.timeout
                )
            except TimeoutError:
                last_error = MCPTimeoutError(f"{operation} timed out")
                logger.warning("Attempt %d timed out: %s", attempt + 1, operation)
            except Exception as e:
                last_error = e
                logger.warning("Attempt %d failed: %s: %s", attempt + 1, operation, e)
            if attempt < self._config.max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        raise last_error or MCPConnectionError(f"{operation} failed after retries")
