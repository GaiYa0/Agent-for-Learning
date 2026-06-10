"""RAG pipeline — end-to-end retrieval augmented generation."""

from learning_assistant.agent.llm.base import BaseLLM
from learning_assistant.models.rag import RAGResponse
from learning_assistant.rag.pipelines.citation_pipeline import CitationPipeline
from learning_assistant.rag.pipelines.retrieval_pipeline import RetrievalPipeline


class RAGPipeline:
    """Orchestrates retrieval, citation building, and LLM generation."""

    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
        llm: BaseLLM,
        citation_pipeline: CitationPipeline | None = None,
    ) -> None:
        self._retrieval = retrieval_pipeline
        self._llm = llm
        self._citations = citation_pipeline or CitationPipeline()

    async def run(self, question: str, top_k: int = 5) -> RAGResponse:
        context = await self._retrieval.run(question, top_k)
        citations = self._citations.build_citations(context.chunks)
        context_text = context.as_text()
        prompt = self._build_prompt(question, context_text)
        messages = [{"role": "user", "content": prompt}]
        response = await self._llm.generate(messages)
        return RAGResponse(
            answer=response.content,
            citations=citations,
            sources=context.sources(),
            retrieved_chunks=len(context.chunks),
            retrieval_time_ms=context.retrieval_time_ms,
        )

    def _build_prompt(self, question: str, context: str) -> str:
        parts = [
            "Answer the question based on the provided context.",
            "Cite sources with numbered references [1], [2], etc.",
            f"\nContext:\n{context}",
            f"\nQuestion: {question}",
        ]
        return "\n".join(parts)
