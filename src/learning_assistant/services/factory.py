"""Service factory — creates service instances from configuration."""

import logging
from collections.abc import Callable

from learning_assistant.config.settings import AppSettings, get_settings
from learning_assistant.services.base import BaseService
from learning_assistant.services.exceptions import ServiceError
from learning_assistant.services.pdf.pdf_service import PDFService
from learning_assistant.services.search.duckduckgo_provider import (
    DuckDuckGoSearchProvider,
)
from learning_assistant.services.search.search_service import SearchService
from learning_assistant.services.search.tavily_provider import TavilySearchProvider

logger = logging.getLogger(__name__)

ServiceCreator = Callable[[], BaseService]


class ServiceFactory:
    """Registry-based factory for creating service instances."""

    def __init__(self) -> None:
        self._creators: dict[str, ServiceCreator] = {}
        self._register_builtins()

    def register(self, name: str, creator: ServiceCreator) -> None:
        self._creators[name] = creator

    def create(self, name: str) -> BaseService:
        creator = self._creators.get(name)
        if creator is None:
            available = ", ".join(sorted(self._creators.keys()))
            raise ServiceError(
                f"Unknown service: '{name}'. Available: [{available}]"
            )
        return creator()

    def create_pdf_service(self) -> PDFService:
        return PDFService()

    def create_search_service(
        self, default_provider: str = "duckduckgo"
    ) -> SearchService:
        service = SearchService(default_provider=default_provider)
        service.register_provider(DuckDuckGoSearchProvider())
        return service

    def create_search_service_from_settings(
        self, settings: AppSettings | None = None
    ) -> SearchService:
        """Build SearchService using AppSettings provider selection."""
        cfg = settings or get_settings()
        ddg = DuckDuckGoSearchProvider()

        if cfg.search_provider == "duckduckgo":
            service = SearchService(default_provider="duckduckgo")
            service.register_provider(ddg)
            return service

        if cfg.search_provider == "tavily":
            service = SearchService(default_provider="tavily")
            service.register_provider(ddg)
            if cfg.tavily_api_key:
                api_key = cfg.get_secret("tavily_api_key")
                service.register_provider(TavilySearchProvider(api_key=api_key))
            else:
                logger.warning(
                    "TAVILY_API_KEY missing; falling back to duckduckgo search"
                )
                service.set_default_provider("duckduckgo")
            return service

        msg = f"Search provider '{cfg.search_provider}' is not supported"
        raise ServiceError(msg)

    def _register_builtins(self) -> None:
        self._creators["pdf"] = PDFService
        self._creators["search"] = lambda: self.create_search_service()
