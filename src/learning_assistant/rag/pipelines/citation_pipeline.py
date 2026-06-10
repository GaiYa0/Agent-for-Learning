"""Citation pipeline — builds numbered citations from retrieved chunks."""

from learning_assistant.models.rag import RAGCitation, RetrievedChunk


class CitationPipeline:
    """Creates numbered citations from retrieved chunks."""

    def build_citations(self, chunks: list[RetrievedChunk]) -> list[RAGCitation]:
        citations: list[RAGCitation] = []
        for idx, chunk in enumerate(chunks, start=1):
            citations.append(
                RAGCitation(
                    index=idx,
                    source=chunk.source,
                    page=chunk.page,
                    chunk_id=chunk.chunk_id,
                    snippet=chunk.content[:200],
                )
            )
        return citations

    def format_citations(self, citations: list[RAGCitation]) -> str:
        lines: list[str] = []
        for c in citations:
            ref = f"[{c.index}]"
            parts = [ref]
            if c.source:
                parts.append(c.source)
            if c.page:
                parts.append(f"p.{c.page}")
            lines.append(" ".join(parts))
        return "\n".join(lines)
