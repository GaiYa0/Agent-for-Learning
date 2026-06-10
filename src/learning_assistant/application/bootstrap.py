"""Application bootstrap — wires config into runtime components."""

from dataclasses import dataclass, field

from learning_assistant.agent.llm.factory import build_llm
from learning_assistant.agent.planner import Planner
from learning_assistant.application.factories.orchestrator_factory import (
    OrchestratorFactory,
)
from learning_assistant.application.factories.usecase_factory import UseCaseFactory
from learning_assistant.application.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
)
from learning_assistant.application.session.conversation_store import ConversationStore
from learning_assistant.application.session.memory_manager import MemoryManager
from learning_assistant.config.settings import AppSettings
from learning_assistant.mcp.client.base import BaseMCPClient
from learning_assistant.rag.embeddings.factory import EmbeddingFactory
from learning_assistant.rag.vectorstores.factory import VectorStoreFactory
from learning_assistant.services.factory import ServiceFactory
from learning_assistant.tools.calculator_tool import CalculatorTool
from learning_assistant.tools.pdf_tool import PDFTool
from learning_assistant.tools.registry import ToolRegistry
from learning_assistant.tools.search_tool import SearchTool


@dataclass
class AppContext:
    """Shared application runtime context."""

    settings: AppSettings
    usecase_factory: UseCaseFactory
    memory_manager: MemoryManager
    mcp_client: BaseMCPClient | None = field(default=None)


def _register_local_tools(registry: ToolRegistry, settings: AppSettings) -> None:
    search_service = ServiceFactory().create_search_service_from_settings(settings)
    registry.register(SearchTool(search_service))
    registry.register(CalculatorTool())
    registry.register(PDFTool())


def build_tool_registry(settings: AppSettings) -> ToolRegistry:
    """Register default local tools (no MCP)."""
    registry = ToolRegistry()
    _register_local_tools(registry, settings)
    return registry


def build_embedding_provider(settings: AppSettings):
    """Create embedding provider (mock until settings-driven selection exists)."""
    _ = settings
    return EmbeddingFactory.create("mock")


def build_vector_store(settings: AppSettings):
    """Create vector store (in-memory until settings-driven selection exists)."""
    _ = settings
    return VectorStoreFactory.create("memory")


def _build_app_context_from_registry(
    settings: AppSettings,
    tool_registry: ToolRegistry,
    *,
    mcp_client: BaseMCPClient | None = None,
) -> AppContext:
    store = ConversationStore()
    memory_manager = MemoryManager(store)
    embedding = build_embedding_provider(settings)
    vector_store = build_vector_store(settings)

    llm = build_llm(settings)
    planner = Planner(llm=llm)
    agent_orch = AgentOrchestrator(
        tool_registry=tool_registry,
        planner=planner,
        memory_manager=memory_manager,
        max_iterations=settings.agent_max_iterations,
        model=settings.openai_model,
    )
    orch_factory = OrchestratorFactory(
        tool_registry, embedding, vector_store, planner
    )
    usecase_factory = UseCaseFactory(
        agent_orch,
        orch_factory.rag_orchestrator(),
        orch_factory.tool_orchestrator(),
        tool_registry,
        vector_store,
        embedding,
    )
    return AppContext(
        settings=settings,
        usecase_factory=usecase_factory,
        memory_manager=memory_manager,
        mcp_client=mcp_client,
    )


async def _register_mcp_tools(
    registry: ToolRegistry,
    settings: AppSettings,
) -> BaseMCPClient | None:
    if not settings.mcp_enabled or not settings.mcp_server_url.strip():
        return None

    from learning_assistant.mcp.factories.mcp_factory import MCPFactory
    from learning_assistant.mcp.tool_provider import MCPToolProvider

    if settings.mcp_transport == "http":
        client = MCPFactory.create_http_client(settings.mcp_server_url)
    elif settings.mcp_transport == "sse":
        client = MCPFactory.create_sse_client(settings.mcp_server_url)
    else:
        client = MCPFactory.create_stdio_client()

    await client.connect()
    provider = MCPToolProvider(client, MCPFactory.create_capability_manager())
    await provider.discover_tools()
    provider.register_to(registry)
    return client


async def build_app_context(settings: AppSettings) -> AppContext:
    """Build full application context, optionally wiring MCP tools."""
    registry = ToolRegistry()
    _register_local_tools(registry, settings)
    mcp_client = await _register_mcp_tools(registry, settings)
    return _build_app_context_from_registry(
        settings, registry, mcp_client=mcp_client
    )


def build_usecase_factory(settings: AppSettings) -> AppContext:
    """Sync bootstrap without MCP (for dependencies and offline tests)."""
    registry = build_tool_registry(settings)
    return _build_app_context_from_registry(settings, registry)
