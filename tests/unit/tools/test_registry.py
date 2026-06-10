"""Tests for ToolRegistry."""

import threading

import pytest

from learning_assistant.tools.exceptions import ToolNotFoundError, ToolRegistrationError
from learning_assistant.tools.registry import ToolRegistry
from tests.unit.tools.conftest import StubTool


@pytest.fixture()
def registry() -> ToolRegistry:
    return ToolRegistry()


class TestRegister:
    def test_register_and_get(self, registry: ToolRegistry) -> None:
        tool = StubTool(tool_name="t1")
        registry.register(tool)
        assert registry.get("t1") is tool

    def test_duplicate_raises(self, registry: ToolRegistry) -> None:
        registry.register(StubTool(tool_name="t1"))
        with pytest.raises(ToolRegistrationError, match="already registered"):
            registry.register(StubTool(tool_name="t1"))

    def test_allow_override(self, registry: ToolRegistry) -> None:
        t1 = StubTool(tool_name="t1", result_content="v1")
        t2 = StubTool(tool_name="t1", result_content="v2")
        registry.register(t1)
        registry.register(t2, allow_override=True)
        assert registry.get("t1") is t2


class TestUnregister:
    def test_unregister_removes(self, registry: ToolRegistry) -> None:
        registry.register(StubTool(tool_name="t1"))
        registry.unregister("t1")
        assert not registry.exists("t1")

    def test_unregister_nonexistent_is_noop(self, registry: ToolRegistry) -> None:
        registry.unregister("ghost")


class TestGet:
    def test_not_found_raises(self, registry: ToolRegistry) -> None:
        with pytest.raises(ToolNotFoundError, match="not found"):
            registry.get("missing")


class TestExists:
    def test_exists_true(self, registry: ToolRegistry) -> None:
        registry.register(StubTool(tool_name="t1"))
        assert registry.exists("t1") is True

    def test_exists_false(self, registry: ToolRegistry) -> None:
        assert registry.exists("nope") is False


class TestListAndCount:
    def test_empty(self, registry: ToolRegistry) -> None:
        assert registry.list_tools() == []
        assert registry.count() == 0

    def test_multiple(self, registry: ToolRegistry) -> None:
        registry.register(StubTool(tool_name="a"))
        registry.register(StubTool(tool_name="b"))
        assert registry.count() == 2
        names = {t.name for t in registry.list_tools()}
        assert names == {"a", "b"}


class TestThreadSafety:
    def test_concurrent_register(self) -> None:
        registry = ToolRegistry()
        errors: list[Exception] = []

        def register_many(prefix: str) -> None:
            try:
                for i in range(50):
                    registry.register(StubTool(tool_name=f"{prefix}_{i}"))
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=register_many, args=("a",))
        t2 = threading.Thread(target=register_many, args=("b",))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        assert len(errors) == 0
        assert registry.count() == 100
