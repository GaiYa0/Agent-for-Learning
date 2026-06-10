"""Metadata builder — generates uniform metadata for chunks."""

from datetime import UTC, datetime

from learning_assistant.models.document import DocumentChunk


class MetadataBuilder:
    """Builds standardized metadata dicts for chunks."""

    def build(
        self,
        chunk: DocumentChunk,
        source: str = "",
        filename: str = "",
    ) -> dict[str, str]:
        return {
            "source": source,
            "filename": filename,
            "page": str(chunk.page_number),
            "chunk_id": chunk.id,
            "chunk_index": str(chunk.chunk_index),
            "created_at": datetime.now(UTC).isoformat(),
        }

    def build_batch(
        self,
        chunks: list[DocumentChunk],
        source: str = "",
        filename: str = "",
    ) -> list[dict[str, str]]:
        return [self.build(c, source, filename) for c in chunks]
