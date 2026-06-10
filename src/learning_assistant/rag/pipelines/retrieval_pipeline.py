"""Retrieval pipeline — retrieves relevant chunks for a query."""

import time

from learning_assistant.models.rag import RetrievedContext
from learning_assistant.rag.retrievers.base import Retriever


class RetrievalPipeline:
    """Runs retrieval and assembles context."""

    def __init__(self, retriever: Retriever) -> None:
        self._retriever = retriever

    async def run(self, query: str, top_k: int = 5) -> RetrievedContext:
        start = time.monotonic()
        chunks = await self._retriever.retrieve(query, top_k)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return RetrievedContext(
            chunks=chunks,
            query=query,
            retrieval_time_ms=elapsed_ms,
        )
