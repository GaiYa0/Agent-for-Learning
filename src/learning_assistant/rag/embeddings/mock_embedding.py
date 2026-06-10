"""Deterministic mock embedding for testing — no network, no randomness."""

import hashlib

from learning_assistant.rag.embeddings.base import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    """Produces deterministic embeddings from text hash. Stable across runs."""

    def __init__(self, dim: int = 384) -> None:
        self._dim = dim

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_query(self, text: str) -> list[float]:
        return self._text_to_vector(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._text_to_vector(t) for t in texts]

    def _text_to_vector(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        raw: list[float] = []
        for i in range(self._dim):
            byte_val = digest[i % len(digest)]
            raw.append((byte_val / 255.0) * 2.0 - 1.0)
        norm = sum(v * v for v in raw) ** 0.5
        return [v / norm for v in raw] if norm > 0 else raw
