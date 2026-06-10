"""Tests for UseCaseFactory and OrchestratorFactory."""

import pytest

from learning_assistant.agent.planner import Planner
from learning_assistant.application.factories.orchestrator_factory import OrchestratorFactory
from learning_assistant.application.factories.usecase_factory import UseCaseFactory
from learning_assistant.application.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
)
from learning_assistant.application.orchestrators.rag_orchestrator import RAGOrchestrator
from learning_assistant.application.orchestrators.tool_orchestrator import ToolOrchestrator
from learning_assistant.application.usecases.chat_usecase import ChatUseCase
from learning_assistant.application.usecases.health_check_usecase import HealthCheckUseCase
from learning_assistant.application.usecases.pdf_upload_usecase import PDFUploadUseCase
from learning_assistant.application.usecases.rag_chat_usecase import RAGChatUseCase
from learning_assistant.application.usecases.search_usecase import SearchUseCase
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM


@pytest.fixture()
def embedding() -> MockEmbeddingProvider:
    return MockEmbeddingProvider(dim=64)


@pytest.fixture()
def store() -> InMemoryVectorStore:
    return InMemoryVectorStore()


@pytest.fixture()
def registry() -> ToolRegistry:
    return ToolRegistry()


@pytest.fixture()
def planner() -> Planner:
    return Planner(llm=MockLLM.with_fixed_reply("ok"))


@pytest.fixture()
def orch_factory(
    registry: ToolRegistry,
    embedding: MockEmbeddingProvider,
    store: InMemoryVectorStore,
    planner: Planner,
) -> OrchestratorFactory:
    return OrchestratorFactory(registry, embedding, store, planner)


@pytest.fixture()
def uc_factory(
    registry: ToolRegistry,
    embedding: MockEmbeddingProvider,
    store: InMemoryVectorStore,
    planner: Planner,
) -> UseCaseFactory:
    orch = OrchestratorFactory(registry, embedding, store, planner)
    return UseCaseFactory(
        orch.agent_orchestrator(),
        orch.rag_orchestrator(),
        orch.tool_orchestrator(),
        registry,
        store,
        embedding,
    )


class TestOrchestratorFactory:
    def test_agent_orchestrator(self, orch_factory: OrchestratorFactory) -> None:
        assert isinstance(orch_factory.agent_orchestrator(), AgentOrchestrator)

    def test_rag_orchestrator(self, orch_factory: OrchestratorFactory) -> None:
        assert isinstance(orch_factory.rag_orchestrator(), RAGOrchestrator)

    def test_tool_orchestrator(self, orch_factory: OrchestratorFactory) -> None:
        assert isinstance(orch_factory.tool_orchestrator(), ToolOrchestrator)


class TestUseCaseFactory:
    def test_chat_usecase(self, uc_factory: UseCaseFactory) -> None:
        assert isinstance(uc_factory.chat_usecase(), ChatUseCase)

    def test_rag_chat_usecase(self, uc_factory: UseCaseFactory) -> None:
        assert isinstance(uc_factory.rag_chat_usecase(), RAGChatUseCase)

    def test_pdf_upload_usecase(self, uc_factory: UseCaseFactory) -> None:
        assert isinstance(uc_factory.pdf_upload_usecase(), PDFUploadUseCase)

    def test_search_usecase(self, uc_factory: UseCaseFactory) -> None:
        assert isinstance(uc_factory.search_usecase(), SearchUseCase)

    def test_health_check_usecase(self, uc_factory: UseCaseFactory) -> None:
        assert isinstance(uc_factory.health_check_usecase(), HealthCheckUseCase)
