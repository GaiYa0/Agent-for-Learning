"""Tests for SourceType, Source, and Citation models."""

import pytest
from pydantic import ValidationError

from learning_assistant.models.source import Source, SourceCitation, SourceType


class TestSourceType:
    def test_all_types_exist(self) -> None:
        assert SourceType.PDF == "pdf"
        assert SourceType.WEB == "web"
        assert SourceType.LLM == "llm"


class TestSource:
    def test_create_with_valid_data(self) -> None:
        src = Source(
            type=SourceType.PDF,
            title="Chapter 1",
            reference="page 3",
            relevance_score=0.95,
            snippet="Some text",
        )
        assert src.type == "pdf"
        assert src.relevance_score == 0.95

    def test_defaults(self) -> None:
        src = Source(type=SourceType.WEB, title="T", reference="https://x.com")
        assert src.relevance_score == 1.0
        assert src.snippet is None

    def test_score_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Source(type=SourceType.PDF, title="T", reference="r", relevance_score=1.5)

    def test_invalid_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Source(type="invalid", title="T", reference="r")

    def test_empty_title_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Source(type=SourceType.PDF, title="", reference="r")

    def test_extra_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Source(type=SourceType.PDF, title="T", reference="r", extra="bad")

    def test_serialization_roundtrip(self) -> None:
        src = Source(type=SourceType.WEB, title="T", reference="r")
        data = src.model_dump()
        restored = Source.model_validate(data)
        assert restored.type == "web"


class TestSourceCitation:
    def test_create_with_valid_data(self) -> None:
        src = Source(type=SourceType.PDF, title="T", reference="p1")
        cit = SourceCitation(index=1, source=src, used_in="paragraph 2")
        assert cit.index == 1
        assert cit.source.title == "T"

    def test_index_zero_rejected(self) -> None:
        src = Source(type=SourceType.PDF, title="T", reference="r")
        with pytest.raises(ValidationError):
            SourceCitation(index=0, source=src)

    def test_serialization_roundtrip(self) -> None:
        src = Source(type=SourceType.LLM, title="T", reference="r")
        cit = SourceCitation(index=1, source=src)
        data = cit.model_dump()
        restored = SourceCitation.model_validate(data)
        assert restored.index == 1
        assert restored.source.type == "llm"

    def test_citation_alias_is_source_citation(self) -> None:
        from learning_assistant.models.source import Citation

        src = Source(type=SourceType.WEB, title="T", reference="r")
        cit = Citation(index=1, source=src)
        assert isinstance(cit, SourceCitation)
