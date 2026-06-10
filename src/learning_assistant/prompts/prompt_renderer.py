"""Jinja2-based template renderer."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape

from learning_assistant.prompts.exceptions import RenderError


class PromptRenderer:
    """Renders Jinja2 templates from a directory."""

    def __init__(self, template_dir: str | Path) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape([]),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=__import__("jinja2").StrictUndefined,
        )

    def render(self, template_name: str, **kwargs: str) -> str:
        try:
            template = self._env.get_template(template_name)
            return template.render(**kwargs)
        except TemplateError as e:
            raise RenderError(f"Failed to render '{template_name}': {e}") from e

    def render_string(self, template_str: str, **kwargs: str) -> str:
        try:
            template = self._env.from_string(template_str)
            return template.render(**kwargs)
        except TemplateError as e:
            raise RenderError(f"Failed to render string template: {e}") from e
