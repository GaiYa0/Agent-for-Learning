"""Tests for HealthCheckUseCase."""

import pytest

from learning_assistant.application.usecases.health_check_usecase import (
    HealthCheckInput,
    HealthCheckUseCase,
)
from learning_assistant.rag.embeddings.mock_embedding import MockEmbeddingProvider
from learning_assistant.rag.vectorstores.in_memory import InMemoryVectorStore
from learning_assistant.tools.registry import ToolRegistry
from tests.mocks.mock_tool import MockTool


@pytest.fixture()
def usecase() -> HealthCheckUseCase:
    registry = ToolRegistry()
    registry.register(MockTool(tool_name="t1"))
    return HealthCheckUseCase(
        registry, InMemoryVectorStore(), MockEmbeddingProvider(dim=64)
    )


class TestHealthCheckUseCase:
    @pytest.mark.asyncio
    async def test_success(self, usecase: HealthCheckUseCase) -> None:
        result = await usecase.execute(HealthCheckInput())
        assert result.success is True
        assert result.data is not None
        assert result.data.system == "ok"
        assert "1 registered" in result.data.tools
        assert "0 chunks" in result.data.vector_store
        assert "dim=64" in result.data.embedding
