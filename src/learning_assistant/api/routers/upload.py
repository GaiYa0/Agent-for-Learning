"""Upload router."""

from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile

from learning_assistant.api.schemas.common import APIResponse
from learning_assistant.api.schemas.upload import UploadResponseDTO

router = APIRouter(prefix="/documents", tags=["Documents"])

_ALLOWED_UPLOAD_SUFFIXES = frozenset({".pdf", ".txt"})


def resolve_upload_suffix(filename: str | None, content: bytes) -> str:
    """Pick a temp-file suffix so PDF uploads route to the PDF parser."""
    if content.startswith(b"%PDF"):
        return ".pdf"
    suffix = Path(filename or "upload").suffix.lower()
    if suffix in _ALLOWED_UPLOAD_SUFFIXES:
        return suffix
    return ".txt"


@router.post(
    "/upload",
    summary="Upload document",
    description="Upload a text/PDF document for indexing.",
    response_model=APIResponse[UploadResponseDTO],
)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),  # noqa: B008
) -> APIResponse[UploadResponseDTO]:
    import tempfile

    from learning_assistant.application.dto.upload_request import UploadRequest as AppUploadRequest

    usecase_factory = request.app.state.usecase_factory
    request_id = getattr(request.state, "request_id", "")

    content = await file.read()
    suffix = resolve_upload_suffix(file.filename, content)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        app_request = AppUploadRequest(
            file_path=tmp_path,
            source=file.filename or "uploaded",
        )
        result = await usecase_factory.pdf_upload_usecase().execute(app_request)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if not result.success:
        return APIResponse(success=False, error=result.error, request_id=request_id)

    dto = UploadResponseDTO(
        filename=file.filename or result.data.filename,
        chunks_indexed=result.data.chunks_indexed,
        document_id=result.data.document_id,
    )
    return APIResponse(success=True, data=dto, request_id=request_id)
