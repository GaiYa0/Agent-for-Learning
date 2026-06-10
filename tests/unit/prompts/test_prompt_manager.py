"""Tests for PromptManager."""

import pytest

from learning_assistant.prompts.exceptions import TemplateNotFoundError
from learning_assistant.prompts.prompt_manager import PromptManager
from learning_assistant.prompts.system_prompt import SystemPrompt


@pytest.fixture()
def manager() -> PromptManager:
    return PromptManager()


class TestPromptManager:
    def test_register_and_get(self, manager: PromptManager) -> None:
        t = SystemPrompt()
        manager.register(t)
        result = manager.get("system", "v1")
        assert result is t

    def test_get_latest(self, manager: PromptManager) -> None:
        t = SystemPrompt()
        manager.register(t)
        result = manager.get("system")
        assert result is t

    def test_get_not_found_raises(self, manager: PromptManager) -> None:
        with pytest.raises(TemplateNotFoundError):
            manager.get("nonexistent")

    def test_get_latest_no_versions_raises(
        self, manager: PromptManager
    ) -> None:
        with pytest.raises(TemplateNotFoundError, match="No versions"):
            manager.get("empty")

    def test_list_templates(self, manager: PromptManager) -> None:
        manager.register(SystemPrompt())
        templates = manager.list_templates()
        assert "system" in templates

    def test_list_versions(self, manager: PromptManager) -> None:
        manager.register(SystemPrompt())
        versions = manager.list_versions("system")
        assert "v1" in versions

    def test_list_versions_empty(self, manager: PromptManager) -> None:
        assert manager.list_versions("nonexistent") == []

    def test_get_latest_uses_numeric_version_order(
        self, manager: PromptManager
    ) -> None:
        from learning_assistant.prompts.base import BasePromptTemplate

        class VersionedPrompt(BasePromptTemplate):
            def __init__(self, name: str, version: str) -> None:
                self._name = name
                self._version = version

            @property
            def name(self) -> str:
                return self._name

            @property
            def version(self) -> str:
                return self._version

            @property
            def required_variables(self) -> set[str]:
                return set()

            def build(self, **kwargs: str) -> str:
                return f"{self._name}:{self._version}"

        manager.register(VersionedPrompt("demo", "v1"))
        manager.register(VersionedPrompt("demo", "v10"))
        manager.register(VersionedPrompt("demo", "v2"))
        latest = manager.get("demo")
        assert latest.version == "v10"
