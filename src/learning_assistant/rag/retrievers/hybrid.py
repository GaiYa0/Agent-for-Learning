"""Hybrid retriever — combines multiple retrieval strategies."""

from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.retrievers.base import Retriever


class HybridRetriever(Retriever):
    """Combines a primary retriever with optional secondary retrievers.

    Extension points for BM25, web search, etc. via add_secondary().
    """

    def __init__(self, primary: Retriever) -> None:
        self._primary = primary
        self._secondaries: list[Retriever] = []

    @staticmethod
    def _dedup_key(chunk: RetrievedChunk) -> str:
        if chunk.chunk_id:
            return chunk.chunk_id
        return f"{chunk.source}:{chunk.page}:{hash(chunk.content)}"

    def add_secondary(self, retriever: Retriever) -> None:
        self._secondaries.append(retriever)

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        primary_results = await self._primary.retrieve(query, top_k)
        seen_ids = {self._dedup_key(c) for c in primary_results}
        all_results = list(primary_results)

        for secondary in self._secondaries:
            secondary_results = await secondary.retrieve(query, top_k)
            for chunk in secondary_results:
                key = self._dedup_key(chunk)
                if key not in seen_ids:
                    seen_ids.add(key)
                    all_results.append(chunk)

        all_results.sort(key=lambda c: c.score, reverse=True)
        return all_results[:top_k]
