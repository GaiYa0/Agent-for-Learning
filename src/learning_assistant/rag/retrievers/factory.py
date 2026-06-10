"""Retriever factory."""

from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.retrievers.base import Retriever
from learning_assistant.rag.retrievers.hybrid import HybridRetriever
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.base import VectorStore


class RetrieverFactory:
    """Creates retriever instances."""

    @classmethod
    def create_similarity(
        cls,
        embedding: EmbeddingProvider,
        store: VectorStore,
        score_threshold: float = 0.0,
    ) -> SimilarityRetriever:
        return SimilarityRetriever(embedding, store, score_threshold)

    @classmethod
    def create_hybrid(cls, primary: Retriever) -> HybridRetriever:
        return HybridRetriever(primary)
