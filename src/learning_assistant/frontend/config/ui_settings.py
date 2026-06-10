"""UI settings — configurable frontend parameters."""

import os
from typing import Literal

from pydantic import BaseModel, Field

from learning_assistant.frontend.i18n import DEFAULT_LOCALE, Language


def _default_api_base_url() -> str:
    return os.getenv("LA_API_BASE_URL", "http://localhost:8000")


def _default_api_key() -> str:
    return os.getenv("LA_API_KEY", "")


def _default_language() -> Language:
    raw = os.getenv("LA_UI_LANGUAGE", DEFAULT_LOCALE)
    if raw in ("zh-CN", "en"):
        return raw  # type: ignore[return-value]
    return DEFAULT_LOCALE


class UISettings(BaseModel):
    language: Language = Field(default_factory=_default_language)
    api_base_url: str = Field(default_factory=_default_api_base_url)
    api_key: str = Field(default_factory=_default_api_key)
    default_top_k: int = Field(ge=1, le=20, default=5)
    default_temperature: float = Field(ge=0.0, le=2.0, default=0.2)
    theme: str = Field(default="light")
    max_history: int = Field(ge=1, default=50)
