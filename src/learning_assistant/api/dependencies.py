"""Dependency injection — provides use case factories to routers."""

from learning_assistant.application.bootstrap import build_usecase_factory
from learning_assistant.application.factories.usecase_factory import UseCaseFactory
from learning_assistant.config.settings import AppSettings, get_settings
from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.vectorstores.base import VectorStore
from learning_assistant.tools.registry import ToolRegistry


def build_usecase_factory_from_settings(
    settings: AppSettings | None = None,
) -> UseCaseFactory:
    """Build UseCaseFactory from application settings."""
    cfg = settings or get_settings()
    return build_usecase_factory(cfg).usecase_factory


def build_usecase_factory_for_tests(
    tool_registry: ToolRegistry,
    embedding_provider: EmbeddingProvider,
    vector_store: VectorStore,
    planner,
) -> UseCaseFactory:
    """Build UseCaseFactory with explicit test doubles (used by API test fixtures)."""
    from learning_assistant.application.factories.orchestrator_factory import (
        OrchestratorFactory,
    )

    orch = OrchestratorFactory(
        tool_registry, embedding_provider, vector_store, planner
    )
    return UseCaseFactory(
        orch.agent_orchestrator(),
        orch.rag_orchestrator(),
        orch.tool_orchestrator(),
        tool_registry,
        vector_store,
        embedding_provider,
    )
