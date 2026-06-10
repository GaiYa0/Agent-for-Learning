"""Response builder — constructs unified API responses."""

from typing import TypeVar

from learning_assistant.api.schemas.common import APIResponse, ErrorDetail, ErrorResponse

T = TypeVar("T")


class ResponseBuilder:
    """Builds standardized API responses."""

    @staticmethod
    def success(data: T, request_id: str = "") -> APIResponse[T]:
        return APIResponse(success=True, data=data, request_id=request_id)

    @staticmethod
    def error(
        message: str, code: str = "INTERNAL_ERROR", request_id: str = ""
    ) -> ErrorResponse:
        return ErrorResponse(
            error=ErrorDetail(code=code, message=message),
            request_id=request_id,
        )
