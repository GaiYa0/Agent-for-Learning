"""Tests for SearchProvider abstract interface."""

import pytest

from learning_assistant.services.search.search_provider import SearchProvider


class TestSearchProviderInterface:
    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            SearchProvider()  # type: ignore[abstract]

    def test_subclass_must_implement(self) -> None:
        class Incomplete(SearchProvider):
            pass

        with pytest.raises(TypeError):
            Incomplete()  # type: ignore[abstract]

    def test_complete_subclass(self) -> None:
        class Complete(SearchProvider):
            @property
            def provider_name(self) -> str:
                return "test"

            async def search(self, query: str, max_results: int = 5):
                from learning_assistant.models.search import SearchResponse

                return SearchResponse(
                    query=query, results=[], provider="test"
                )

        provider = Complete()
        assert provider.provider_name == "test"
