"""Embedding provider factory."""

from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider


class EmbeddingFactory:
    """Creates embedding providers from configuration."""

    _providers: dict[str, type[EmbeddingProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_cls: type[EmbeddingProvider]) -> None:
        cls._providers[name] = provider_cls

    @classmethod
    def create(cls, name: str, dim: int = 384) -> EmbeddingProvider:
        if name == "mock":
            return MockEmbeddingProvider(dim=dim)
        provider_cls = cls._providers.get(name)
        if provider_cls is None:
            available = ["mock", *sorted(cls._providers.keys())]
            raise ValueError(
                f"Unknown embedding provider: '{name}'. Available: {available}"
            )
        return provider_cls()

    @classmethod
    def available(cls) -> list[str]:
        return ["mock", *sorted(cls._providers.keys())]
