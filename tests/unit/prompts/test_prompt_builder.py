"""Tests for PromptBuilder and PromptContext."""

from learning_assistant.models.chat import ChatMessage, MessageRole
from learning_assistant.prompts.prompt_builder import PromptBuilder, PromptContext


class TestPromptBuilder:
    def test_empty_context(self) -> None:
        builder = PromptBuilder()
        result = builder.build(PromptContext())
        assert result == ""

    def test_system_only(self) -> None:
        builder = PromptBuilder()
        ctx = PromptContext(system="You are helpful.")
        result = builder.build(ctx)
        assert "[System]" in result
        assert "You are helpful." in result

    def test_user_only(self) -> None:
        builder = PromptBuilder()
        ctx = PromptContext(user="What is Python?")
        result = builder.build(ctx)
        assert "[User]" in result
        assert "What is Python?" in result

    def test_all_parts(self) -> None:
        builder = PromptBuilder()
        ctx = PromptContext(
            system="System msg",
            user="User msg",
            history=[
                ChatMessage(role=MessageRole.USER, content="Hi"),
                ChatMessage(role=MessageRole.ASSISTANT, content="Hello"),
            ],
            tool_context="Tool result",
            search_context="Search result",
            document_context="Document text",
        )
        result = builder.build(ctx)
        assert "[System]" in result
        assert "[Document Context]" in result
        assert "[Search Results]" in result
        assert "[Tool Results]" in result
        assert "[Conversation History]" in result
        assert "[User]" in result
        assert "user: Hi" in result
        assert "assistant: Hello" in result

    def test_ordering(self) -> None:
        builder = PromptBuilder()
        ctx = PromptContext(
            system="S",
            user="U",
            document_context="D",
            search_context="SR",
            tool_context="T",
        )
        result = builder.build(ctx)
        s_pos = result.index("[System]")
        d_pos = result.index("[Document Context]")
        sr_pos = result.index("[Search Results]")
        t_pos = result.index("[Tool Results]")
        u_pos = result.index("[User]")
        assert s_pos < d_pos < sr_pos < t_pos < u_pos
