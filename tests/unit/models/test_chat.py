"""Tests for ChatMessage and Conversation models."""

import pytest
from pydantic import ValidationError

from learning_assistant.models.chat import ChatMessage, Conversation, MessageRole


class TestMessageRole:
    def test_all_roles_exist(self) -> None:
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.TOOL == "tool"


class TestChatMessage:
    def test_create_with_valid_data(self) -> None:
        msg = ChatMessage(role=MessageRole.USER, content="Hello")
        assert msg.content == "Hello"
        assert msg.role == "user"
        assert msg.id is not None
        assert msg.timestamp is not None

    def test_defaults(self) -> None:
        msg = ChatMessage(role=MessageRole.ASSISTANT, content="Hi")
        assert msg.tool_call_id is None
        assert msg.metadata == {}

    def test_invalid_role_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ChatMessage(role="invalid", content="Hi")

    def test_with_tool_fields(self) -> None:
        msg = ChatMessage(
            role=MessageRole.TOOL,
            content="result",
            tool_call_id="call-1",
        )
        assert msg.tool_call_id == "call-1"

    def test_metadata_accepts_non_string_values(self) -> None:
        msg = ChatMessage(
            role=MessageRole.USER,
            content="Hi",
            metadata={"tokens": 42, "model": "gpt-4o"},
        )
        assert msg.metadata["tokens"] == 42

    def test_extra_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ChatMessage(role=MessageRole.USER, content="Hi", extra="bad")

    def test_serialization_roundtrip(self) -> None:
        msg = ChatMessage(role=MessageRole.USER, content="Hello")
        data = msg.model_dump()
        restored = ChatMessage.model_validate(data)
        assert restored.content == msg.content
        assert restored.role == msg.role


class TestConversation:
    def test_create_empty(self) -> None:
        conv = Conversation()
        assert conv.messages == []
        assert conv.document_ids == []
        assert conv.message_count() == 0
        assert conv.last_message() is None

    def test_add_message(self) -> None:
        conv = Conversation()
        msg = ChatMessage(role=MessageRole.USER, content="Hello")
        conv.add_message(msg)
        assert conv.message_count() == 1
        assert conv.last_message().content == "Hello"

    def test_add_multiple_messages(self) -> None:
        conv = Conversation()
        conv.add_message(ChatMessage(role=MessageRole.USER, content="Q1"))
        conv.add_message(ChatMessage(role=MessageRole.ASSISTANT, content="A1"))
        conv.add_message(ChatMessage(role=MessageRole.USER, content="Q2"))
        assert conv.message_count() == 3
        assert conv.last_message().content == "Q2"

    def test_updated_at_changes_on_add(self) -> None:
        conv = Conversation()
        t1 = conv.updated_at
        conv.add_message(ChatMessage(role=MessageRole.USER, content="Hi"))
        assert conv.updated_at >= t1

    def test_serialization_roundtrip(self) -> None:
        conv = Conversation(document_ids=["doc-1"])
        conv.add_message(ChatMessage(role=MessageRole.USER, content="Hi"))
        data = conv.model_dump()
        restored = Conversation.model_validate(data)
        assert restored.message_count() == 1
        assert restored.document_ids == ["doc-1"]
