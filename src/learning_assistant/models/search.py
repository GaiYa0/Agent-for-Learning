"""Web search result and response models."""

from pydantic import Field

from learning_assistant.models.base import DomainModel
from learning_assistant.models.source import SourceType


class SearchResult(DomainModel):
    """A single search result from a web search."""

    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    snippet: str = ""
    score: float = Field(ge=0.0, le=1.0, default=0.0)
    published_date: str | None = None
    source_type: SourceType = SourceType.WEB


class SearchResponse(DomainModel):
    """Aggregated search results from a provider."""

    query: str = Field(min_length=1)
    results: list[SearchResult] = Field(default_factory=list)
    provider: str = Field(min_length=1)
    duration_ms: int = Field(ge=0, default=0)

    def sorted_results(self) -> list[SearchResult]:
        return sorted(self.results, key=lambda r: r.score, reverse=True)

    def top_result(self) -> SearchResult | None:
        sorted_r = self.sorted_results()
        return sorted_r[0] if sorted_r else None

    def result_count(self) -> int:
        return len(self.results)
