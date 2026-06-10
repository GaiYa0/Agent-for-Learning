"""Text chunking strategies for document processing."""

from uuid import uuid4

from learning_assistant.models.document import DocumentChunk
from learning_assistant.services.exceptions import ChunkError


class FixedSizeChunker:
    """Splits text into fixed-size chunks with overlap, respecting sentence boundaries."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        if chunk_size <= 0:
            raise ChunkError(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0:
            raise ChunkError(f"chunk_overlap must be non-negative, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ChunkError(
                f"chunk_overlap ({chunk_overlap}) must be < chunk_size ({chunk_size})"
            )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[str]:
        if not text.strip():
            return []
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            if end < len(text):
                sentence_break = self._find_sentence_break(chunk)
                if sentence_break > 0:
                    chunk = text[start : start + sentence_break]
                    end = start + sentence_break
            if chunk.strip():
                chunks.append(chunk)
            if end >= len(text):
                break
            start = end - self.chunk_overlap
        return chunks

    def chunk_document(
        self,
        text: str,
        document_id: str = "",
        page_map: dict[int, str] | None = None,
    ) -> list[DocumentChunk]:
        raw_chunks = self.chunk_text(text)
        doc_id = document_id or str(uuid4())
        result: list[DocumentChunk] = []
        offset = 0
        for idx, chunk_text in enumerate(raw_chunks):
            start_char = text.find(chunk_text, offset)
            if start_char == -1:
                start_char = offset
            end_char = start_char + len(chunk_text)
            page = self._resolve_page(start_char, page_map) if page_map else 1
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

    def _find_sentence_break(self, text: str) -> int:
        for i in range(len(text) - 1, max(len(text) // 2, 0), -1):
            if text[i] in ".!?\n":
                return i + 1
        return 0

    def _resolve_page(self, char_offset: int, page_map: dict[int, str]) -> int:
        cumulative = 0
        for page_num, page_text in sorted(page_map.items()):
            cumulative += len(page_text)
            if char_offset < cumulative:
                return page_num
        return max(page_map.keys()) if page_map else 1
