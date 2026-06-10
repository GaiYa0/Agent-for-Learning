"""Orchestrator factory — creates orchestrators with injected dependencies."""

from learning_assistant.agent.planner import Planner
from learning_assistant.application.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
)
from learning_assistant.application.orchestrators.rag_orchestrator import RAGOrchestrator
from learning_assistant.application.orchestrators.tool_orchestrator import ToolOrchestrator
from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.pipelines.retrieval_pipeline import RetrievalPipeline
from learning_assistant.rag.retrievers.similarity import SimilarityRetriever
from learning_assistant.rag.vectorstores.base import VectorStore
from learning_assistant.tools.registry import ToolRegistry


class OrchestratorFactory:
    """Creates orchestrator instances."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        planner: Planner,
    ) -> None:
        self._registry = tool_registry
        self._embedding = embedding_provider
        self._store = vector_store
        self._planner = planner

    def agent_orchestrator(self) -> AgentOrchestrator:
        return AgentOrchestrator(self._registry, self._planner)

    def rag_orchestrator(self) -> RAGOrchestrator:
        retriever = SimilarityRetriever(self._embedding, self._store)
        pipeline = RetrievalPipeline(retriever)
        return RAGOrchestrator(self._embedding, self._store, pipeline)

    def tool_orchestrator(self) -> ToolOrchestrator:
        return ToolOrchestrator(self._registry)
