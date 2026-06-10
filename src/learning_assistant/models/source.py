"""Source attribution and citation models."""

from enum import StrEnum

from pydantic import Field

from learning_assistant.models.base import DomainModel


class SourceType(StrEnum):
    PDF = "pdf"
    WEB = "web"
    LLM = "llm"


class Source(DomainModel):
    """An information source used to compose an answer."""

    type: SourceType
    title: str = Field(min_length=1)
    reference: str = Field(min_length=1)
    relevance_score: float = Field(ge=0.0, le=1.0, default=1.0)
    snippet: str | None = None


class SourceCitation(DomainModel):
    """Citation linking answer text to a structured Source (agent attribution)."""

    index: int = Field(ge=1)
    source: Source
    used_in: str = ""


# Backward-compatible alias — prefer SourceCitation in new code
Citation = SourceCitation
