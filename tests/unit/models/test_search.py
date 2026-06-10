"""Tests for SearchResult and SearchResponse models."""

import pytest
from pydantic import ValidationError

from learning_assistant.models.search import SearchResponse, SearchResult


class TestSearchResult:
    def test_create_with_valid_data(self) -> None:
        sr = SearchResult(
            title="Result",
            url="https://example.com",
            snippet="A snippet",
            score=0.9,
        )
        assert sr.title == "Result"
        assert sr.score == 0.9

    def test_defaults(self) -> None:
        sr = SearchResult(title="R", url="https://x.com")
        assert sr.snippet == ""
        assert sr.score == 0.0
        assert sr.published_date is None
        assert sr.source_type == "web"

    def test_score_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SearchResult(title="R", url="https://x.com", score=1.5)
        with pytest.raises(ValidationError):
            SearchResult(title="R", url="https://x.com", score=-0.1)

    def test_empty_title_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SearchResult(title="", url="https://x.com")

    def test_extra_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SearchResult(title="R", url="https://x.com", extra="bad")

    def test_serialization_roundtrip(self) -> None:
        sr = SearchResult(title="R", url="https://x.com", score=0.8)
        data = sr.model_dump()
        restored = SearchResult.model_validate(data)
        assert restored.score == 0.8


class TestSearchResponse:
    def test_create_with_valid_data(self) -> None:
        resp = SearchResponse(
            query="test",
            results=[],
            provider="tavily",
            duration_ms=100,
        )
        assert resp.query == "test"
        assert resp.result_count() == 0
        assert resp.top_result() is None

    def test_top_result_returns_highest_score(self) -> None:
        resp = SearchResponse(
            query="q",
            results=[
                SearchResult(title="Low", url="https://a.com", score=0.3),
                SearchResult(title="High", url="https://b.com", score=0.9),
                SearchResult(title="Mid", url="https://c.com", score=0.6),
            ],
            provider="tavily",
        )
        top = resp.top_result()
        assert top is not None
        assert top.title == "High"
        # Input order preserved; sorting is explicit via sorted_results()
        assert resp.results[0].title == "Low"

    def test_sorted_results_by_score(self) -> None:
        resp = SearchResponse(
            query="q",
            results=[
                SearchResult(title="Low", url="https://a.com", score=0.3),
                SearchResult(title="High", url="https://b.com", score=0.9),
            ],
            provider="tavily",
        )
        sorted_r = resp.sorted_results()
        assert sorted_r[0].title == "High"
        assert sorted_r[1].title == "Low"

    def test_result_count(self) -> None:
        resp = SearchResponse(
            query="q",
            results=[
                SearchResult(title="A", url="https://a.com"),
                SearchResult(title="B", url="https://b.com"),
            ],
            provider="tavily",
        )
        assert resp.result_count() == 2

    def test_empty_query_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SearchResponse(query="", results=[], provider="tavily")

    def test_negative_duration_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SearchResponse(query="q", results=[], provider="tavily", duration_ms=-1)

    def test_serialization_roundtrip(self) -> None:
        resp = SearchResponse(
            query="q",
            results=[SearchResult(title="R", url="https://x.com")],
            provider="tavily",
        )
        data = resp.model_dump()
        restored = SearchResponse.model_validate(data)
        assert restored.result_count() == 1
