"""Tests for ToolFactory."""

import pytest

from learning_assistant.tools.exceptions import ToolRegistrationError
from learning_assistant.tools.tool_factory import ToolFactory
from tests.unit.tools.conftest import StubTool


@pytest.fixture()
def factory() -> ToolFactory:
    return ToolFactory()


class TestToolFactory:
    def test_register_and_create(self, factory: ToolFactory) -> None:
        factory.register("stub", lambda: StubTool(tool_name="stub"))
        tool = factory.create("stub")
        assert tool.name == "stub"

    def test_create_unknown_raises(self, factory: ToolFactory) -> None:
        with pytest.raises(ToolRegistrationError, match="Unknown tool"):
            factory.create("nope")

    def test_duplicate_register_raises(self, factory: ToolFactory) -> None:
        factory.register("t", lambda: StubTool())
        with pytest.raises(ToolRegistrationError, match="already registered"):
            factory.register("t", lambda: StubTool())

    def test_available_tools(self, factory: ToolFactory) -> None:
        factory.register("a", lambda: StubTool(tool_name="a"))
        factory.register("b", lambda: StubTool(tool_name="b"))
        assert factory.available_tools() == ["a", "b"]
