"""Exception middleware — catches unhandled errors and returns structured JSON."""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from learning_assistant.api.schemas.common import ErrorDetail, ErrorResponse

logger = logging.getLogger("api.exception")


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "")
            logger.exception("Unhandled error: %s", exc)
            body = ErrorResponse(
                error=ErrorDetail(code="INTERNAL_ERROR", message=str(exc)),
                request_id=request_id,
            )
            return JSONResponse(status_code=500, content=body.model_dump())
