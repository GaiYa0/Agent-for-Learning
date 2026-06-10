"""Tests for ConversationMemory."""

from learning_assistant.agent.memory import ConversationMemory


class TestConversationMemory:
    def test_empty(self) -> None:
        mem = ConversationMemory()
        assert mem.message_count() == 0
        assert mem.get_messages() == []

    def test_add_user_message(self) -> None:
        mem = ConversationMemory()
        msg = mem.add_user_message("Hello")
        assert msg.role == "user"
        assert mem.message_count() == 1

    def test_add_assistant_message(self) -> None:
        mem = ConversationMemory()
        mem.add_assistant_message("Hi there")
        assert mem.get_messages()[0].role == "assistant"

    def test_add_tool_message(self) -> None:
        mem = ConversationMemory()
        mem.add_tool_message("result", tool_call_id="c1")
        msg = mem.get_messages()[0]
        assert msg.role == "tool"
        assert msg.tool_call_id == "c1"

    def test_get_history_dicts(self) -> None:
        mem = ConversationMemory()
        mem.add_user_message("Q")
        mem.add_assistant_message("A")
        dicts = mem.get_history_dicts()
        assert len(dicts) == 2
        assert dicts[0]["role"] == "user"
        assert dicts[1]["role"] == "assistant"

    def test_clear(self) -> None:
        mem = ConversationMemory()
        mem.add_user_message("Q")
        mem.clear()
        assert mem.message_count() == 0

    def test_trim(self) -> None:
        mem = ConversationMemory(max_messages=3)
        for i in range(5):
            mem.add_user_message(f"msg {i}")
        assert mem.message_count() == 3
        assert mem.get_messages()[0].content == "msg 2"
