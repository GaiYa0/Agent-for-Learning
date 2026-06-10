"""Tests for RAGChatUseCase."""

import pytest

from learning_assistant.agent.planner import Planner
from learning_assistant.application.dto.chat_request import ChatRequest
from learning_assistant.application.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
)
from learning_assistant.application.orchestrators.rag_orchestrator import RAGOrchestrator
from learning_assistant.application.usecases.rag_chat_usecase import RAGChatUseCase
from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.pipelines.retrieval_pipeline import RetrievalPipeline
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM


@pytest.mark.asyncio
async def test_rag_chat_success() -> None:
    emb = MockEmbeddingProvider(dim=64)
    store = InMemoryVectorStore()
    chunks = [RetrievedChunk(content="Python is great", score=1.0, chunk_id="1")]
    embs = await emb.embed_documents(["Python is great"])
    await store.add_documents(chunks, embs)
    retriever = SimilarityRetriever(emb, store)
    pipeline = RetrievalPipeline(retriever)
    rag_orch = RAGOrchestrator(emb, store, pipeline)
    llm = MockLLM.with_react_sequence(
        ["Thought: I know.\nFinal Answer: Python is great. [1]"]
    )
    agent_orch = AgentOrchestrator(ToolRegistry(), Planner(llm=llm))
    usecase = RAGChatUseCase(agent_orch, rag_orch)
    req = ChatRequest(session_id="s1", message="What is Python?", use_rag=True)
    result = await usecase.execute(req)
    assert result.success is True
    assert result.data is not None
    assert "Python" in result.data.answer


@pytest.mark.asyncio
async def test_rag_chat_empty_message_rejected() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ChatRequest(session_id="s1", message="")
