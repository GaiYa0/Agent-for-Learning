"""Tests for AgentState, ResponseMetadata, and AgentResponse models."""

import pytest
from pydantic import ValidationError

from learning_assistant.models.agent import AgentResponse, AgentState, ResponseMetadata
from learning_assistant.models.chat import ChatMessage, Conversation, MessageRole
from learning_assistant.models.source import Source, SourceType


class TestAgentState:
    def test_create_with_defaults(self) -> None:
        state = AgentState()
        assert state.iteration == 0
        assert state.max_iterations == 5
        assert state.tools_used == []
        assert state.can_continue() is True

    def test_can_continue_at_limit(self) -> None:
        state = AgentState(max_iterations=3)
        state.iteration = 3
        assert state.can_continue() is False

    def test_can_continue_below_limit(self) -> None:
        state = AgentState(max_iterations=3)
        state.iteration = 2
        assert state.can_continue() is True

    def test_increment_iteration(self) -> None:
        state = AgentState()
        assert state.iteration == 0
        state.increment_iteration()
        assert state.iteration == 1
        state.increment_iteration()
        assert state.iteration == 2

    def test_custom_conversation(self) -> None:
        conv = Conversation()
        conv.add_message(ChatMessage(role=MessageRole.USER, content="Hi"))
        state = AgentState(conversation=conv)
        assert state.conversation.message_count() == 1

    def test_max_iterations_zero_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AgentState(max_iterations=0)

    def test_negative_iteration_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AgentState(iteration=-1)

    def test_extra_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AgentState(extra="bad")


class TestResponseMetadata:
    def test_create_with_valid_data(self) -> None:
        meta = ResponseMetadata(
            iterations=2,
            tools_used=["pdf_reader"],
            total_duration_ms=1500,
            model="gpt-4o",
        )
        assert meta.iterations == 2

    def test_defaults(self) -> None:
        meta = ResponseMetadata(iterations=0)
        assert meta.tools_used == []
        assert meta.total_duration_ms == 0
        assert meta.model == ""

    def test_negative_iterations_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ResponseMetadata(iterations=-1)


class TestAgentResponse:
    def test_create_with_valid_data(self) -> None:
        resp = AgentResponse(answer="The answer is 42.")
        assert resp.answer == "The answer is 42."
        assert resp.id is not None
        assert resp.created_at is not None

    def test_defaults(self) -> None:
        resp = AgentResponse(answer="ok")
        assert resp.citations == []
        assert resp.sources == []
        assert resp.metadata.iterations == 0

    def test_with_sources_and_citations(self) -> None:
        src = Source(type=SourceType.PDF, title="Book", reference="p5")
        resp = AgentResponse(
            answer="Based on the PDF...",
            sources=[src],
            metadata=ResponseMetadata(iterations=1, tools_used=["pdf_reader"]),
        )
        assert len(resp.sources) == 1
        assert resp.metadata.tools_used == ["pdf_reader"]

    def test_extra_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AgentResponse(answer="ok", extra="bad")

    def test_serialization_roundtrip(self) -> None:
        resp = AgentResponse(answer="ok")
        data = resp.model_dump()
        restored = AgentResponse.model_validate(data)
        assert restored.answer == "ok"
        assert restored.id == resp.id
