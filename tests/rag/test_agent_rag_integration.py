"""Agent + RAG integration tests — all offline, all mocks."""

import pytest

from learning_assistant.agent.core import ReActAgent
from learning_assistant.agent.executor import ActionExecutor
from learning_assistant.agent.memory import ConversationMemory
from learning_assistant.agent.planner import Planner
from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.pipelines.retrieval_pipeline import RetrievalPipeline
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore
from learning_assistant.tools.manager import ToolManager
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM


@pytest.mark.asyncio
async def test_agent_with_rag_context() -> None:
    emb = MockEmbeddingProvider(dim=64)
    store = InMemoryVectorStore()
    chunks = [
        RetrievedChunk(
            content="Machine learning is a subset of AI.",
            score=1.0,
            chunk_id="1",
            source="textbook",
        ),
    ]
    embs = await emb.embed_documents(["Machine learning is a subset of AI."])
    await store.add_documents(chunks, embs)
    retriever = SimilarityRetriever(emb, store)
    retrieval = RetrievalPipeline(retriever)
    ctx = await retrieval.run("What is ML?", top_k=1)
    context_text = ctx.as_text()
    llm = MockLLM.with_react_sequence([
        "Thought: Based on context.\nFinal Answer: Machine learning is a subset of AI. [1]",
    ])
    registry = ToolRegistry()
    manager = ToolManager(registry)
    planner = Planner(llm=llm)
    executor = ActionExecutor(manager)
    agent = ReActAgent(
        planner=planner,
        executor=executor,
        memory=ConversationMemory(),
        max_iterations=3,
        context=context_text,
    )
    answer = await agent.run("What is ML?")
    assert "machine learning" in answer.lower()
