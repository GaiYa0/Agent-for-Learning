"""Tests for ToolDefinition, ToolCall, and ToolResult models."""

import pytest
from pydantic import ValidationError

from learning_assistant.models.tool import ToolCall, ToolDefinition, ToolResult


class TestToolDefinition:
    def test_create_with_valid_data(self) -> None:
        td = ToolDefinition(
            name="pdf_reader",
            description="Read PDF files",
            parameters={"file_path": {"type": "string"}},
            category="pdf",
        )
        assert td.name == "pdf_reader"

    def test_empty_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ToolDefinition(name="", description="d", category="c")

    def test_empty_description_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ToolDefinition(name="t", description="", category="c")

    def test_default_parameters(self) -> None:
        td = ToolDefinition(name="t", description="d", category="c")
        assert td.parameters == {}

    def test_extra_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ToolDefinition(name="t", description="d", category="c", extra="bad")

    def test_serialization_roundtrip(self) -> None:
        td = ToolDefinition(name="t", description="d", category="c")
        data = td.model_dump()
        restored = ToolDefinition.model_validate(data)
        assert restored.name == "t"


class TestToolCall:
    def test_create_with_valid_data(self) -> None:
        tc = ToolCall(tool_name="pdf_reader", arguments={"path": "/a.pdf"})
        assert tc.tool_name == "pdf_reader"
        assert tc.id is not None
        assert tc.timestamp is not None

    def test_defaults(self) -> None:
        tc = ToolCall(tool_name="t")
        assert tc.arguments == {}

    def test_empty_tool_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ToolCall(tool_name="")

    def test_serialization_roundtrip(self) -> None:
        tc = ToolCall(tool_name="t", arguments={"k": "v"})
        data = tc.model_dump()
        restored = ToolCall.model_validate(data)
        assert restored.tool_name == "t"
        assert restored.arguments == {"k": "v"}


class TestToolResult:
    def test_success_result(self) -> None:
        tr = ToolResult(
            tool_call_id="call-1",
            success=True,
            content="done",
            duration_ms=100,
        )
        assert tr.is_success() is True
        assert tr.is_failure() is False

    def test_failure_result(self) -> None:
        tr = ToolResult(
            tool_call_id="call-1",
            success=False,
            error="timeout",
            duration_ms=5000,
        )
        assert tr.is_failure() is True
        assert tr.is_success() is False

    def test_defaults(self) -> None:
        tr = ToolResult(tool_call_id="c", success=True, duration_ms=0)
        assert tr.content == ""
        assert tr.error is None

    def test_negative_duration_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ToolResult(tool_call_id="c", success=True, duration_ms=-1)

    def test_serialization_roundtrip(self) -> None:
        tr = ToolResult(
            tool_call_id="c", success=True, content="ok", duration_ms=50
        )
        data = tr.model_dump()
        restored = ToolResult.model_validate(data)
        assert restored.is_success() is True
