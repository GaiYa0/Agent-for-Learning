"""Chat router."""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from learning_assistant.api.schemas.chat import ChatRequest, ChatResponseDTO, ResponseMetadataDTO
from learning_assistant.api.schemas.common import APIResponse
from learning_assistant.api.streaming import stream_event_to_sse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    summary="Chat with agent",
    description="Send a message and get a response from the learning assistant agent.",
    response_model=APIResponse[ChatResponseDTO],
)
async def chat(
    request: Request,
    body: ChatRequest,
) -> APIResponse[ChatResponseDTO]:
    from learning_assistant.application.dto.chat_request import ChatRequest as AppChatRequest

    usecase_factory = request.app.state.usecase_factory
    app_request = AppChatRequest(
        session_id=body.session_id,
        message=body.message,
        use_rag=body.use_rag,
    )

    if body.use_rag:
        result = await usecase_factory.rag_chat_usecase().execute(app_request)
    else:
        result = await usecase_factory.chat_usecase().execute(app_request)

    request_id = getattr(request.state, "request_id", "")

    if not result.success:
        return APIResponse(success=False, error=result.error, request_id=request_id)

    data = result.data
    dto = ChatResponseDTO(
        answer=data.answer,
        citations=data.citations,
        metadata=ResponseMetadataDTO(
            iterations=data.metadata.iterations,
            tools_used=data.metadata.tools_used,
            retrieval_time_ms=data.metadata.retrieval_time_ms,
            total_duration_ms=data.metadata.total_duration_ms,
            model=data.metadata.model,
        ),
    )
    return APIResponse(success=True, data=dto, request_id=request_id)


@router.post(
    "/stream",
    summary="Stream chat with agent",
    description="Send a message and stream the agent response via Server-Sent Events.",
)
async def chat_stream(
    request: Request,
    body: ChatRequest,
) -> StreamingResponse:
    from learning_assistant.application.dto.chat_request import ChatRequest as AppChatRequest

    usecase_factory = request.app.state.usecase_factory
    app_request = AppChatRequest(
        session_id=body.session_id,
        message=body.message,
        use_rag=body.use_rag,
    )

    async def event_generator():
        async for event in usecase_factory.chat_usecase().execute_stream(app_request):
            yield stream_event_to_sse(event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
