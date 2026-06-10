"""Similarity retriever — embed query, search vector store, filter by threshold."""

from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.retrievers.base import Retriever
from learning_assistant.rag.vectorstores.base import VectorStore


class SimilarityRetriever(Retriever):
    """Retrieves chunks by embedding similarity."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        score_threshold: float = 0.0,
    ) -> None:
        self._embedding = embedding_provider
        self._store = vector_store
        self._threshold = score_threshold

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        query_emb = await self._embedding.embed_query(query)
        results = await self._store.similarity_search_with_score(query_emb, top_k)
        return [
            chunk.model_copy(update={"score": score})
            for chunk, score in results
            if score >= self._threshold
        ]
