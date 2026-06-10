"""Tests for HybridRetriever — offline only."""

import pytest

from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.retrievers.hybrid import HybridRetriever
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore


@pytest.mark.asyncio
async def test_hybrid_primary_only() -> None:
    emb = MockEmbeddingProvider(dim=64)
    store = InMemoryVectorStore()
    chunks = [RetrievedChunk(content="test", score=1.0, chunk_id="1")]
    embs = await emb.embed_documents(["test"])
    await store.add_documents(chunks, embs)
    primary = SimilarityRetriever(emb, store)
    hybrid = HybridRetriever(primary)
    results = await hybrid.retrieve("test", top_k=1)
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_hybrid_with_secondary() -> None:
    emb = MockEmbeddingProvider(dim=64)
    store1 = InMemoryVectorStore()
    store2 = InMemoryVectorStore()
    chunks1 = [RetrievedChunk(content="from primary", score=1.0, chunk_id="1")]
    chunks2 = [RetrievedChunk(content="from secondary", score=0.9, chunk_id="2")]
    embs1 = await emb.embed_documents(["from primary"])
    embs2 = await emb.embed_documents(["from secondary"])
    await store1.add_documents(chunks1, embs1)
    await store2.add_documents(chunks2, embs2)
    primary = SimilarityRetriever(emb, store1)
    secondary = SimilarityRetriever(emb, store2)
    hybrid = HybridRetriever(primary)
    hybrid.add_secondary(secondary)
    results = await hybrid.retrieve("from primary", top_k=5)
    assert len(results) >= 1
