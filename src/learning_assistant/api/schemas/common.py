"""Common API schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Unified API response envelope."""

    success: bool
    data: T | None = None
    error: str | None = None
    request_id: str = ""


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    request_id: str = ""
