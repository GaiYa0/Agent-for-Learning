"""Chat use case — simple agent conversation."""

from collections.abc import AsyncIterator

from learning_assistant.agent.stream_events import StreamEvent
from learning_assistant.application.dto.chat_request import ChatRequest
from learning_assistant.application.dto.chat_response import ChatResponse
from learning_assistant.application.dto.common import Result
from learning_assistant.application.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
)
from learning_assistant.application.usecases.base import BaseUseCase


class ChatUseCase(BaseUseCase[ChatRequest, ChatResponse]):
    """Executes a simple chat with the agent."""

    def __init__(self, agent_orchestrator: AgentOrchestrator) -> None:
        self._agent = agent_orchestrator

    async def execute(self, input_dto: ChatRequest) -> Result[ChatResponse]:
        if not input_dto.message.strip():
            return Result.fail("Message must not be empty")
        try:
            agent_response = await self._agent.run(
                input_dto.message,
                session_id=input_dto.session_id,
            )
            return Result.ok(
                ChatResponse(
                    answer=agent_response.answer,
                    metadata=agent_response.metadata,
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
            async for event in self._agent.run_streaming(
                input_dto.message,
                session_id=input_dto.session_id,
            ):
                yield event
        except Exception as e:
            yield StreamEvent(kind="error", message=str(e))
