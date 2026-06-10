"""Tests for RAGState."""

from learning_assistant.frontend.state.rag_state import RAGState
from learning_assistant.models.rag import RAGCitation


class TestRAGCitation:
    def test_create(self) -> None:
        c = RAGCitation(index=1, source="doc.pdf", page=5, snippet="text")
        assert c.index == 1
        assert c.source == "doc.pdf"
        assert c.page == 5


class TestRAGState:
    def test_empty(self) -> None:
        state = RAGState()
        assert state.citations == []
        assert state.retrieved_chunks == 0

    def test_set_citations(self) -> None:
        state = RAGState()
        state.set_citations([
            {"source": "doc.pdf", "page": "5", "snippet": "text"},
            {"source": "web", "page": "0"},
        ])
        assert len(state.citations) == 2
        assert state.citations[0].index == 1
        assert state.citations[0].source == "doc.pdf"
        assert state.citations[0].page == 5
        assert state.citations[1].index == 2

    def test_clear(self) -> None:
        state = RAGState()
        state.add_user_message("Q")
        state.set_citations([{"source": "a", "page": "1"}])
        state.retrieved_chunks = 3
        state.clear()
        assert state.messages == []
        assert state.citations == []
        assert state.retrieved_chunks == 0

    def test_inherits_chat_state(self) -> None:
        state = RAGState()
        state.add_user_message("Q")
        state.add_assistant_message("A")
        assert len(state.messages) == 2
