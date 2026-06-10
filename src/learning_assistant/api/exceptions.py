"""API-layer exception hierarchy."""

from fastapi import HTTPException, status


class APIError(HTTPException):
    """Base for all API errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR) -> None:
        super().__init__(status_code=status_code, detail=detail)


class BadRequestError(APIError):
    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class NotFoundError(APIError):
    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedError(APIError):
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(APIError):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class InternalError(APIError):
    def __init__(self, detail: str = "Internal server error") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
