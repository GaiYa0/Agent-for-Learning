"""Health router."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from learning_assistant.api.schemas.common import APIResponse
from learning_assistant.application.usecases.health_check_usecase import HealthCheckInput

router = APIRouter(tags=["Health"])

_start_time = datetime.now(UTC)


@router.get(
    "/health",
    summary="Health check",
    description="Returns system health status.",
    response_model=APIResponse[dict[str, object]],
)
async def health_check(request: Request) -> APIResponse[dict[str, object]]:
    uptime = (datetime.now(UTC) - _start_time).total_seconds()
    settings = getattr(request.app.state, "settings", None)
    version = settings.app_version if settings else "0.1.0"

    data: dict[str, object] = {
        "status": "ok",
        "version": version,
        "uptime_seconds": int(uptime),
    }

    factory = getattr(request.app.state, "usecase_factory", None)
    if factory is not None:
        result = await factory.health_check_usecase().execute(HealthCheckInput())
        if result.success and result.data is not None:
            data["components"] = result.data.model_dump()

    return APIResponse(success=True, data=data)
