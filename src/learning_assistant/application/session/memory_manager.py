"""Memory manager — syncs conversation store with agent memory."""

from learning_assistant.agent.memory import ConversationMemory
from learning_assistant.application.session.conversation_store import ConversationStore


class MemoryManager:
    """Synchronizes ConversationStore with ConversationMemory."""

    def __init__(self, store: ConversationStore) -> None:
        self._store = store
        self._memories: dict[str, ConversationMemory] = {}

    def get_memory(self, session_id: str) -> ConversationMemory:
        if session_id not in self._memories:
            if not self._store.exists(session_id):
                self._store.create(session_id)
            self._memories[session_id] = ConversationMemory()
            self._sync_from_store(session_id)
        return self._memories[session_id]

    def sync_to_store(self, session_id: str) -> None:
        memory = self._memories.get(session_id)
        if memory is None:
            return
        if not self._store.exists(session_id):
            self._store.create(session_id)
        record = self._store.get(session_id)
        if record is None:
            return
        record.messages = memory.get_messages()

    def _sync_from_store(self, session_id: str) -> None:
        record = self._store.get(session_id)
        if record is None:
            return
        memory = self._memories[session_id]
        for msg in record.messages:
            if msg.role == "user":
                memory.add_user_message(msg.content)
            elif msg.role == "assistant":
                memory.add_assistant_message(msg.content)
            elif msg.role == "tool":
                memory.add_tool_message(msg.content, msg.tool_call_id or "")

    def delete_memory(self, session_id: str) -> None:
        self._memories.pop(session_id, None)
