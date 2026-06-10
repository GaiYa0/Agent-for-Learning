"""Tests for ChatState."""

from learning_assistant.frontend.state.chat_state import ChatMessage, ChatState


class TestChatMessage:
    def test_create(self) -> None:
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.thinking == ""
        assert msg.citations == []


class TestChatState:
    def test_empty(self) -> None:
        state = ChatState()
        assert state.messages == []
        assert state.is_loading is False
        assert state.error is None

    def test_add_user_message(self) -> None:
        state = ChatState()
        state.add_user_message("Hello")
        assert len(state.messages) == 1
        assert state.messages[0].role == "user"
        assert state.messages[0].content == "Hello"

    def test_add_assistant_message(self) -> None:
        state = ChatState()
        state.add_assistant_message("Hi!", thinking="I should greet back.")
        assert len(state.messages) == 1
        assert state.messages[0].role == "assistant"
        assert state.messages[0].thinking == "I should greet back."

    def test_add_with_citations(self) -> None:
        state = ChatState()
        state.add_assistant_message("Answer", citations=[{"source": "doc.pdf", "page": "1"}])
        assert state.messages[0].citations == [{"source": "doc.pdf", "page": "1"}]

    def test_clear(self) -> None:
        state = ChatState()
        state.add_user_message("Q")
        state.set_loading(True)
        state.set_error("err")
        state.clear()
        assert state.messages == []
        assert state.is_loading is False
        assert state.error is None

    def test_set_loading(self) -> None:
        state = ChatState()
        state.set_loading(True)
        assert state.is_loading is True

    def test_set_error(self) -> None:
        state = ChatState()
        state.set_error("bad")
        assert state.error == "bad"
