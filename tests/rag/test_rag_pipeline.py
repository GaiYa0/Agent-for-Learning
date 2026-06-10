"""Tests for RAGPipeline — offline, all mocks."""

import pytest

from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.pipelines.rag_pipeline import RAGPipeline
from learning_assistant.rag.pipelines.retrieval_pipeline import RetrievalPipeline
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore
from tests.mocks.mock_llm import MockLLM


@pytest.mark.asyncio
async def test_rag_pipeline_end_to_end() -> None:
    emb = MockEmbeddingProvider(dim=64)
    store = InMemoryVectorStore()
    chunks = [
        RetrievedChunk(content="Python is a language.", score=1.0, chunk_id="1", source="book"),
    ]
    embs = await emb.embed_documents(["Python is a language."])
    await store.add_documents(chunks, embs)
    retriever = SimilarityRetriever(emb, store)
    retrieval = RetrievalPipeline(retriever)
    llm = MockLLM.with_fixed_reply("Python is a programming language [1].")
    pipeline = RAGPipeline(retrieval, llm)
    response = await pipeline.run("What is Python?", top_k=1)
    assert "Python" in response.answer
    assert len(response.citations) >= 1
    assert response.retrieved_chunks >= 1
    assert response.retrieval_time_ms >= 0
