"""Shared DTO types — Result wrapper and common fields."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """Unified result wrapper for all use case outputs."""

    success: bool
    data: T | None = None
    error: str | None = None

    @classmethod
    def ok(cls, data: T) -> "Result[T]":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "Result[T]":
        return cls(success=False, error=error)


class PaginationParams(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=20)
