"""Tests for ServiceFactory."""

import pytest

from learning_assistant.services.exceptions import ServiceError
from learning_assistant.services.factory import ServiceFactory
from learning_assistant.services.pdf.pdf_service import PDFService
from learning_assistant.services.search.search_service import SearchService


@pytest.fixture()
def factory() -> ServiceFactory:
    return ServiceFactory()


class TestServiceFactory:
    def test_create_pdf_service(self, factory: ServiceFactory) -> None:
        svc = factory.create_pdf_service()
        assert isinstance(svc, PDFService)
        assert svc.service_name == "pdf"

    def test_create_search_service(self, factory: ServiceFactory) -> None:
        svc = factory.create_search_service()
        assert isinstance(svc, SearchService)
        assert svc.service_name == "search"

    def test_create_by_name_pdf(self, factory: ServiceFactory) -> None:
        svc = factory.create("pdf")
        assert isinstance(svc, PDFService)

    def test_create_by_name_search(self, factory: ServiceFactory) -> None:
        svc = factory.create("search")
        assert isinstance(svc, SearchService)

    def test_create_unknown_raises(self, factory: ServiceFactory) -> None:
        with pytest.raises(ServiceError, match="Unknown service"):
            factory.create("nonexistent")

    def test_register_custom_creator(self, factory: ServiceFactory) -> None:
        sentinel = PDFService()
        factory.register("custom", lambda: sentinel)
        assert factory.create("custom") is sentinel

    def test_override_builtin(self, factory: ServiceFactory) -> None:
        sentinel = PDFService()
        factory.register("pdf", lambda: sentinel)
        assert factory.create("pdf") is sentinel

    def test_search_service_has_default_provider(
        self, factory: ServiceFactory
    ) -> None:
        svc = factory.create_search_service()
        provider = svc.get_provider()
        assert provider.provider_name == "duckduckgo"

    def test_create_search_from_settings_tavily_with_key(
        self, factory: ServiceFactory, valid_env_vars: dict[str, str]
    ) -> None:
        from learning_assistant.config.settings import AppSettings

        settings = AppSettings()  # type: ignore[call-arg]
        svc = factory.create_search_service_from_settings(settings)
        assert svc.get_provider().provider_name == "tavily"

    def test_create_search_from_settings_tavily_without_key(
        self, monkeypatch: pytest.MonkeyPatch, factory: ServiceFactory
    ) -> None:
        from learning_assistant.config.settings import AppSettings, get_settings

        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("SEARCH_PROVIDER", "tavily")
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        get_settings.cache_clear()
        settings = AppSettings()  # type: ignore[call-arg]
        svc = factory.create_search_service_from_settings(settings)
        assert svc.get_provider().provider_name == "duckduckgo"
        get_settings.cache_clear()
