"""Tests for MemoryManager."""

import pytest

from learning_assistant.application.session.conversation_store import ConversationStore
from learning_assistant.application.session.memory_manager import MemoryManager
from learning_assistant.models.chat import ChatMessage, MessageRole


@pytest.fixture()
def store() -> ConversationStore:
    return ConversationStore()


@pytest.fixture()
def manager(store: ConversationStore) -> MemoryManager:
    return MemoryManager(store)


class TestMemoryManager:
    def test_get_memory_creates_new(
        self, manager: MemoryManager, store: ConversationStore
    ) -> None:
        store.create("s1")
        mem = manager.get_memory("s1")
        assert mem.message_count() == 0

    def test_get_memory_returns_same(
        self, manager: MemoryManager, store: ConversationStore
    ) -> None:
        store.create("s1")
        m1 = manager.get_memory("s1")
        m2 = manager.get_memory("s1")
        assert m1 is m2

    def test_sync_from_store(
        self, manager: MemoryManager, store: ConversationStore
    ) -> None:
        store.create("s1")
        store.add_message("s1", ChatMessage(role=MessageRole.USER, content="Hi"))
        store.add_message(
            "s1", ChatMessage(role=MessageRole.ASSISTANT, content="Hello")
        )
        mem = manager.get_memory("s1")
        assert mem.message_count() == 2

    def test_sync_to_store(
        self, manager: MemoryManager, store: ConversationStore
    ) -> None:
        store.create("s1")
        mem = manager.get_memory("s1")
        mem.add_user_message("Q")
        mem.add_assistant_message("A")
        manager.sync_to_store("s1")
        record = store.get("s1")
        assert record is not None
        assert len(record.messages) == 2

    def test_delete_memory(
        self, manager: MemoryManager, store: ConversationStore
    ) -> None:
        store.create("s1")
        manager.get_memory("s1")
        manager.delete_memory("s1")
        assert "s1" not in manager._memories
