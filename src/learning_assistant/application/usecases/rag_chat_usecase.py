"""RAG chat use case — agent conversation with retrieval context."""

from collections.abc import AsyncIterator

from learning_assistant.agent.stream_events import StreamEvent
from learning_assistant.application.dto.chat_request import ChatRequest
from learning_assistant.application.dto.chat_response import ChatResponse
from learning_assistant.application.dto.common import Result
from learning_assistant.application.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
)
from learning_assistant.application.orchestrators.rag_orchestrator import RAGOrchestrator
from learning_assistant.application.usecases.base import BaseUseCase
from learning_assistant.models.agent import ResponseMetadata


class RAGChatUseCase(BaseUseCase[ChatRequest, ChatResponse]):
    """Executes a chat with RAG context."""

    def __init__(
        self,
        agent_orchestrator: AgentOrchestrator,
        rag_orchestrator: RAGOrchestrator,
    ) -> None:
        self._agent = agent_orchestrator
        self._rag = rag_orchestrator

    async def execute(self, input_dto: ChatRequest) -> Result[ChatResponse]:
        if not input_dto.message.strip():
            return Result.fail("Message must not be empty")
        try:
            top_k = input_dto.top_k or 5
            ctx = await self._rag.retrieve(input_dto.message, top_k=top_k)
            citations = self._rag.get_citation_pipeline().build_citations(ctx.chunks)
            agent_response = await self._agent.run(
                input_dto.message,
                context=ctx.as_text(),
                session_id=input_dto.session_id,
            )
            metadata = agent_response.metadata.model_copy(
                update={"retrieval_time_ms": ctx.retrieval_time_ms}
            )
            return Result.ok(
                ChatResponse(
                    answer=agent_response.answer,
                    citations=citations,
                    metadata=metadata,
                )
            )
        except Exception as e:
            return Result.fail(str(e))

    async def execute_stream(
        self, input_dto: ChatRequest
    ) -> AsyncIterator[StreamEvent]:
        if not input_dto.message.strip():
            yield StreamEvent(kind="error", message="Message must not be empty")
            return
        try:
            top_k = input_dto.top_k or 5
            ctx = await self._rag.retrieve(input_dto.message, top_k=top_k)
            citations = self._rag.get_citation_pipeline().build_citations(ctx.chunks)
            async for event in self._agent.run_streaming(
                input_dto.message,
                context=ctx.as_text(),
                session_id=input_dto.session_id,
                citations=citations,
                retrieval_time_ms=ctx.retrieval_time_ms,
            ):
                yield event
        except Exception as e:
            yield StreamEvent(kind="error", message=str(e))
