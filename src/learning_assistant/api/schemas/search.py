"""Search API schemas."""

from pydantic import BaseModel, Field

from learning_assistant.models.search import SearchResult


class SearchRequestDTO(BaseModel):
    query: str = Field(min_length=1)
    max_results: int = Field(ge=1, le=20, default=5)


class SearchResponseDTO(BaseModel):
    query: str
    results: list[SearchResult] = []
    provider: str = ""
