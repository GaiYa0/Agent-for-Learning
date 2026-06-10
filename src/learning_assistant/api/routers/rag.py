"""RAG router."""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from learning_assistant.api.schemas.common import APIResponse
from learning_assistant.api.schemas.rag import RAGChatRequest, RAGChatResponseDTO
from learning_assistant.api.streaming import stream_event_to_sse

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post(
    "/chat",
    summary="RAG-enhanced chat",
    description="Chat with retrieval-augmented generation context.",
    response_model=APIResponse[RAGChatResponseDTO],
)
async def rag_chat(
    request: Request,
    body: RAGChatRequest,
) -> APIResponse[RAGChatResponseDTO]:
    from learning_assistant.application.dto.chat_request import ChatRequest as AppChatRequest

    usecase_factory = request.app.state.usecase_factory
    app_request = AppChatRequest(
        session_id=body.session_id,
        message=body.message,
        use_rag=True,
        top_k=body.top_k,
    )
    result = await usecase_factory.rag_chat_usecase().execute(app_request)
    request_id = getattr(request.state, "request_id", "")

    if not result.success:
        return APIResponse(success=False, error=result.error, request_id=request_id)

    data = result.data
    dto = RAGChatResponseDTO(
        answer=data.answer,
        citations=data.citations,
        retrieved_chunks=len(data.citations),
        retrieval_time_ms=data.metadata.retrieval_time_ms,
    )
    return APIResponse(success=True, data=dto, request_id=request_id)


@router.post(
    "/chat/stream",
    summary="Stream RAG-enhanced chat",
    description="Chat with retrieval-augmented context, streaming via Server-Sent Events.",
)
async def rag_chat_stream(
    request: Request,
    body: RAGChatRequest,
) -> StreamingResponse:
    from learning_assistant.application.dto.chat_request import ChatRequest as AppChatRequest

    usecase_factory = request.app.state.usecase_factory
    app_request = AppChatRequest(
        session_id=body.session_id,
        message=body.message,
        use_rag=True,
        top_k=body.top_k,
    )

    async def event_generator():
        async for event in usecase_factory.rag_chat_usecase().execute_stream(app_request):
            yield stream_event_to_sse(event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
