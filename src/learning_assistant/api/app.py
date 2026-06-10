"""FastAPI application factory."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from learning_assistant.api.lifespan import lifespan
from learning_assistant.api.middleware.exception import ExceptionMiddleware
from learning_assistant.api.middleware.logging import LoggingMiddleware
from learning_assistant.api.middleware.metrics import MetricsMiddleware
from learning_assistant.api.middleware.request_id import RequestIdMiddleware
from learning_assistant.api.routers import chat, health, rag, search, upload
from learning_assistant.api.security.api_key import verify_api_key
from learning_assistant.config.settings import get_settings

_auth_dependency = [Depends(verify_api_key)]


def create_app(title: str = "Learning Assistant API", version: str = "0.1.0") -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=title,
        version=version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    cors_origins = settings.get_cors_origins()
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health.router)
    app.include_router(chat.router, dependencies=_auth_dependency)
    app.include_router(rag.router, dependencies=_auth_dependency)
    app.include_router(upload.router, dependencies=_auth_dependency)
    app.include_router(search.router, dependencies=_auth_dependency)

    return app
