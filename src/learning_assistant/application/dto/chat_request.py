"""Chat request DTO."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    use_rag: bool = False
    top_k: int | None = Field(default=None, ge=1, le=20)
