"""Chunk processor — splits text into chunks with overlap."""

from uuid import uuid4

from learning_assistant.models.document import DocumentChunk
from learning_assistant.rag.exceptions import IndexingError


class ChunkProcessor:
    """Splits text into fixed-size chunks with sentence-boundary awareness."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        if chunk_size <= 0:
            raise IndexingError(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise IndexingError(
                f"chunk_overlap must be in [0, chunk_size), got {chunk_overlap}"
            )
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def process(
        self, text: str, document_id: str = "", page: int = 1
    ) -> list[DocumentChunk]:
        if not text.strip():
            return []
        doc_id = document_id or str(uuid4())
        raw_chunks = self._split_text(text)
        result: list[DocumentChunk] = []
        offset = 0
        for idx, chunk_text in enumerate(raw_chunks):
            start_char = text.find(chunk_text, offset)
            if start_char == -1:
                start_char = offset
            end_char = start_char + len(chunk_text)
            result.append(
                DocumentChunk(
                    document_id=doc_id,
                    content=chunk_text,
                    page_number=page,
                    chunk_index=idx,
                    start_char=start_char,
                    end_char=end_char,
                )
            )
            offset = end_char
        return result

    def _split_text(self, text: str) -> list[str]:
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + self._chunk_size, len(text))
            chunk = text[start:end]
            if end < len(text):
                break_point = self._find_sentence_break(chunk)
                if break_point > 0:
                    chunk = text[start : start + break_point]
                    end = start + break_point
            if chunk.strip():
                chunks.append(chunk)
            if end >= len(text):
                break
            start = end - self._chunk_overlap
        return chunks

    def _find_sentence_break(self, text: str) -> int:
        for i in range(len(text) - 1, max(len(text) // 2, 0), -1):
            if text[i] in ".!?\n":
                return i + 1
        return 0
