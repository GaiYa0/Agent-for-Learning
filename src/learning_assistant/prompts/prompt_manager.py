"""Prompt template registry and version manager."""

import re

from learning_assistant.prompts.base import BasePromptTemplate
from learning_assistant.prompts.exceptions import TemplateNotFoundError

_VERSION_RE = re.compile(r"^v(\d+)$")


class PromptManager:
    """Manages prompt templates with version support."""

    def __init__(self) -> None:
        self._templates: dict[str, BasePromptTemplate] = {}

    def register(self, template: BasePromptTemplate) -> None:
        key = self._key(template.name, template.version)
        self._templates[key] = template

    def get(self, name: str, version: str = "latest") -> BasePromptTemplate:
        if version == "latest":
            return self._get_latest(name)
        key = self._key(name, version)
        template = self._templates.get(key)
        if template is None:
            raise TemplateNotFoundError(f"Template not found: {name} v{version}")
        return template

    def list_templates(self) -> list[str]:
        names: set[str] = set()
        for key in self._templates:
            names.add(key.rsplit(":", 1)[0])
        return sorted(names)

    def list_versions(self, name: str) -> list[str]:
        prefix = f"{name}:"
        versions = [k.split(":")[1] for k in self._templates if k.startswith(prefix)]
        return sorted(versions, key=self._version_sort_key)

    def _get_latest(self, name: str) -> BasePromptTemplate:
        versions = self.list_versions(name)
        if not versions:
            raise TemplateNotFoundError(f"No versions found for template: {name}")
        latest = max(versions, key=self._version_sort_key)
        return self._templates[self._key(name, latest)]

    @staticmethod
    def _version_sort_key(version: str) -> tuple[int, str]:
        match = _VERSION_RE.match(version)
        if match:
            return (int(match.group(1)), version)
        return (0, version)

    @staticmethod
    def _key(name: str, version: str) -> str:
        return f"{name}:{version}"
