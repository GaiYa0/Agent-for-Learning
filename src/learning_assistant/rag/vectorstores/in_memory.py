"""In-memory vector store using numpy for cosine similarity."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

from learning_assistant.models.rag import RetrievedChunk  # noqa: TC001
from learning_assistant.rag.vectorstores.base import VectorStore


class InMemoryVectorStore(VectorStore):
    """Vector store backed by in-memory numpy arrays. Ideal for dev/test/CI."""

    def __init__(self) -> None:
        self._chunks: list[RetrievedChunk] = []
        self._embeddings: list[NDArray[np.float64]] = []

    async def add_documents(
        self,
        chunks: list[RetrievedChunk],
        embeddings: list[list[float]],
    ) -> None:
        for chunk, emb in zip(chunks, embeddings, strict=True):
            self._chunks.append(chunk)
            self._embeddings.append(np.array(emb, dtype=np.float64))

    async def delete_documents(self, chunk_ids: list[str]) -> None:
        ids_to_delete = set(chunk_ids)
        new_chunks: list[RetrievedChunk] = []
        new_embeddings: list[NDArray[np.float64]] = []
        for chunk, emb in zip(self._chunks, self._embeddings, strict=False):
            if chunk.chunk_id not in ids_to_delete:
                new_chunks.append(chunk)
                new_embeddings.append(emb)
        self._chunks = new_chunks
        self._embeddings = new_embeddings

    async def similarity_search(
        self, embedding: list[float], top_k: int = 5
    ) -> list[RetrievedChunk]:
        results = await self.similarity_search_with_score(embedding, top_k)
        return [chunk for chunk, _ in results]

    async def similarity_search_with_score(
        self, embedding: list[float], top_k: int = 5
    ) -> list[tuple[RetrievedChunk, float]]:
        if not self._embeddings:
            return []
        query = np.array(embedding, dtype=np.float64)
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            return []
        scores: list[float] = []
        for stored in self._embeddings:
            stored_norm = np.linalg.norm(stored)
            if stored_norm == 0:
                scores.append(0.0)
            else:
                scores.append(float(np.dot(query, stored) / (query_norm * stored_norm)))
        indexed = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self._chunks[i], score) for i, score in indexed]

    async def count(self) -> int:
        return len(self._chunks)

    async def clear(self) -> None:
        self._chunks.clear()
        self._embeddings.clear()
