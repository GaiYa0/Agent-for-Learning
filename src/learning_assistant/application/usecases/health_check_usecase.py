"""Health check use case — reports system component status."""

from pydantic import BaseModel

from learning_assistant.application.dto.common import Result
from learning_assistant.application.usecases.base import BaseUseCase
from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.vectorstores.base import VectorStore
from learning_assistant.tools.registry import ToolRegistry


class HealthStatus(BaseModel):
    system: str = "ok"
    tools: str = "unknown"
    vector_store: str = "unknown"
    embedding: str = "unknown"


class HealthCheckInput(BaseModel):
    pass


class HealthCheckUseCase(BaseUseCase[HealthCheckInput, HealthStatus]):
    """Checks health of all system components."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        vector_store: VectorStore,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self._registry = tool_registry
        self._store = vector_store
        self._embedding = embedding_provider

    async def execute(self, input_dto: HealthCheckInput) -> Result[HealthStatus]:
        try:
            tool_count = self._registry.count()
            store_count = await self._store.count()
            dim = self._embedding.dimension
            return Result.ok(
                HealthStatus(
                    tools=f"ok ({tool_count} registered)",
                    vector_store=f"ok ({store_count} chunks)",
                    embedding=f"ok (dim={dim})",
                )
            )
        except Exception as e:
            return Result.fail(str(e))
