"""ChromaDB vector store adapter — Adapter pattern, no direct Chroma dependency in business code."""

from learning_assistant.models.rag import RetrievedChunk
from learning_assistant.rag.exceptions import VectorStoreError
from learning_assistant.rag.vectorstores.base import VectorStore


class ChromaVectorStore(VectorStore):
    """Adapter for ChromaDB. Requires chromadb package."""

    def __init__(self, collection_name: str = "default", persist_dir: str | None = None) -> None:
        try:
            import chromadb

            if persist_dir:
                client = chromadb.PersistentClient(path=persist_dir)
            else:
                client = chromadb.Client()
            self._collection = client.get_or_create_collection(collection_name)
        except ImportError as e:
            raise VectorStoreError(
                "chromadb not installed. Install with: pip install chromadb"
            ) from e

    async def add_documents(
        self, chunks: list[RetrievedChunk], embeddings: list[list[float]]
    ) -> None:
        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [c.metadata for c in chunks]
        self._collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    async def delete_documents(self, chunk_ids: list[str]) -> None:
        self._collection.delete(ids=chunk_ids)

    async def similarity_search(
        self, embedding: list[float], top_k: int = 5
    ) -> list[RetrievedChunk]:
        results = await self.similarity_search_with_score(embedding, top_k)
        return [chunk for chunk, _ in results]

    async def similarity_search_with_score(
        self, embedding: list[float], top_k: int = 5
    ) -> list[tuple[RetrievedChunk, float]]:
        results = self._collection.query(query_embeddings=[embedding], n_results=top_k)
        chunks: list[tuple[RetrievedChunk, float]] = []
        if results and results["ids"]:
            for i, doc_id in enumerate(results["ids"][0]):
                content = results["documents"][0][i] if results["documents"] else ""
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                dist = results["distances"][0][i] if results["distances"] else 0.0
                score = max(0.0, 1.0 - dist)
                chunks.append((
                    RetrievedChunk(content=content, score=score, metadata=meta, chunk_id=doc_id),
                    score,
                ))
        return chunks

    async def count(self) -> int:
        result: int = self._collection.count()
        return result

    async def clear(self) -> None:
        self._collection.delete(where={})
