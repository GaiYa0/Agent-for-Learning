"""Application lifespan — startup and shutdown hooks."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from learning_assistant.api.security.api_key import configure_api_keys
from learning_assistant.application.bootstrap import build_app_context
from learning_assistant.config.logging import setup_logging
from learning_assistant.config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(settings.log_level)  # type: ignore[arg-type]
    configure_api_keys(settings.get_api_keys())
    ctx = await build_app_context(settings)
    app.state.settings = ctx.settings
    app.state.usecase_factory = ctx.usecase_factory
    app.state.memory_manager = ctx.memory_manager
    app.state.mcp_client = ctx.mcp_client
    yield
    if ctx.mcp_client is not None:
        await ctx.mcp_client.disconnect()
