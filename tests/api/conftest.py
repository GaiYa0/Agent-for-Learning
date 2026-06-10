"""Shared fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient

from learning_assistant.agent.planner import Planner
from learning_assistant.api.app import create_app
from learning_assistant.api.security.api_key import configure_api_keys
from learning_assistant.application.bootstrap import AppContext
from learning_assistant.application.factories.orchestrator_factory import OrchestratorFactory
from learning_assistant.application.factories.usecase_factory import UseCaseFactory
from learning_assistant.application.session.conversation_store import ConversationStore
from learning_assistant.application.session.memory_manager import MemoryManager
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM
from tests.mocks.mock_tool import MockTool


@pytest.fixture(autouse=True)
def _reset_api_keys() -> None:
    configure_api_keys(set())


@pytest.fixture()
def registry() -> ToolRegistry:
    r = ToolRegistry()
    r.register(MockTool(tool_name="web_search", result_content="search results"))
    return r


@pytest.fixture()
def embedding() -> MockEmbeddingProvider:
    return MockEmbeddingProvider(dim=64)


@pytest.fixture()
def store() -> InMemoryVectorStore:
    return InMemoryVectorStore()


@pytest.fixture()
def usecase_factory(
    registry: ToolRegistry,
    embedding: MockEmbeddingProvider,
    store: InMemoryVectorStore,
) -> UseCaseFactory:
    llm = MockLLM.with_react_sequence(
        ["Thought: I know.\nFinal Answer: The answer is 42."]
    )
    planner = Planner(llm=llm)
    orch = OrchestratorFactory(registry, embedding, store, planner)
    return UseCaseFactory(
        orch.agent_orchestrator(),
        orch.rag_orchestrator(),
        orch.tool_orchestrator(),
        registry,
        store,
        embedding,
    )


@pytest.fixture()
def client(
    usecase_factory: UseCaseFactory,
    valid_env_vars: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    from learning_assistant.config.settings import get_settings

    def _mock_build(settings):
        return AppContext(
            settings=settings,
            usecase_factory=usecase_factory,
            memory_manager=MemoryManager(ConversationStore()),
        )

    async def _mock_build_async(settings):
        return _mock_build(settings)

    monkeypatch.setattr(
        "learning_assistant.api.lifespan.build_app_context",
        _mock_build_async,
    )
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
