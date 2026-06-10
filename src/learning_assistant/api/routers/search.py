"""Search router."""

from fastapi import APIRouter, Request

from learning_assistant.api.schemas.common import APIResponse
from learning_assistant.api.schemas.search import SearchRequestDTO, SearchResponseDTO

router = APIRouter(prefix="/search", tags=["Search"])


@router.post(
    "",
    summary="Web search",
    description="Search the web for information.",
    response_model=APIResponse[SearchResponseDTO],
)
async def search(
    request: Request,
    body: SearchRequestDTO,
) -> APIResponse[SearchResponseDTO]:
    from learning_assistant.application.dto.search_request import (
        SearchRequest as AppSearchRequest,
    )

    usecase_factory = request.app.state.usecase_factory
    app_request = AppSearchRequest(
        query=body.query,
        max_results=body.max_results,
    )
    result = await usecase_factory.search_usecase().execute(app_request)
    request_id = getattr(request.state, "request_id", "")

    if not result.success:
        return APIResponse(success=False, error=result.error, request_id=request_id)

    dto = SearchResponseDTO(
        query=result.data.query,
        results=result.data.results,
        provider=result.data.provider,
    )
    return APIResponse(success=True, data=dto, request_id=request_id)
