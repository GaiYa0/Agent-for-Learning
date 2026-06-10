"""Tests for API key protection on production routes."""

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
from learning_assistant.config.settings import get_settings
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_llm import MockLLM
from tests.mocks.mock_tool import MockTool


@pytest.fixture()
def protected_client(
    valid_env_vars: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    registry = ToolRegistry()
    registry.register(MockTool(tool_name="web_search", result_content="results"))
    embedding = MockEmbeddingProvider(dim=64)
    store = InMemoryVectorStore()
    llm = MockLLM.with_react_sequence(
        ["Thought: ok.\nFinal Answer: hi"]
    )
    planner = Planner(llm=llm)
    orch = OrchestratorFactory(registry, embedding, store, planner)
    usecase_factory = UseCaseFactory(
        orch.agent_orchestrator(),
        orch.rag_orchestrator(),
        orch.tool_orchestrator(),
        registry,
        store,
        embedding,
    )

    def _mock_build(settings):
        configure_api_keys({"prod-key"})
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
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as client:
        yield client
    configure_api_keys(set())
    get_settings.cache_clear()


def test_health_is_public(protected_client: TestClient) -> None:
    resp = protected_client.get("/health")
    assert resp.status_code == 200


def test_chat_requires_api_key(protected_client: TestClient) -> None:
    resp = protected_client.post(
        "/chat",
        json={"session_id": "s1", "message": "hi", "use_rag": False},
    )
    assert resp.status_code == 401


def test_chat_with_valid_api_key(protected_client: TestClient) -> None:
    resp = protected_client.post(
        "/chat",
        json={"session_id": "s1", "message": "hi", "use_rag": False},
        headers={"X-API-Key": "prod-key"},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
