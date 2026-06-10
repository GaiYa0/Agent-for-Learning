"""Use case factory — creates use cases with injected dependencies."""

from typing import TYPE_CHECKING

from learning_assistant.application.usecases.chat_usecase import ChatUseCase
from learning_assistant.application.usecases.health_check_usecase import (
    HealthCheckUseCase,
)
from learning_assistant.application.usecases.pdf_upload_usecase import PDFUploadUseCase
from learning_assistant.application.usecases.rag_chat_usecase import RAGChatUseCase
from learning_assistant.application.usecases.search_usecase import SearchUseCase
from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.vectorstores.base import VectorStore
from learning_assistant.tools.registry import ToolRegistry

if TYPE_CHECKING:
    from learning_assistant.application.orchestrators.agent_orchestrator import (
        AgentOrchestrator,
    )
    from learning_assistant.application.orchestrators.rag_orchestrator import RAGOrchestrator
    from learning_assistant.application.orchestrators.tool_orchestrator import ToolOrchestrator


class UseCaseFactory:
    """Creates use case instances with injected dependencies."""

    def __init__(
        self,
        agent_orch: "AgentOrchestrator",
        rag_orch: "RAGOrchestrator",
        tool_orch: "ToolOrchestrator",
        tool_registry: ToolRegistry,
        vector_store: VectorStore,
        embedding_provider: EmbeddingProvider,
    ) -> None:

        self._agent = agent_orch
        self._rag = rag_orch
        self._tool = tool_orch
        self._registry = tool_registry
        self._store = vector_store
        self._embedding = embedding_provider

    def chat_usecase(self) -> ChatUseCase:
        return ChatUseCase(self._agent)

    def rag_chat_usecase(self) -> RAGChatUseCase:
        return RAGChatUseCase(self._agent, self._rag)

    def pdf_upload_usecase(self) -> PDFUploadUseCase:
        return PDFUploadUseCase(self._rag)

    def search_usecase(self) -> SearchUseCase:
        return SearchUseCase(self._tool)

    def health_check_usecase(self) -> HealthCheckUseCase:
        return HealthCheckUseCase(self._registry, self._store, self._embedding)
