"""Logging middleware — logs request/response with latency."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.monotonic()
        request_id = getattr(request.state, "request_id", "-")
        logger.info("[%s] %s %s", request_id, request.method, request.url.path)
        response = await call_next(request)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info("[%s] %d %dms", request_id, response.status_code, elapsed_ms)
        return response
