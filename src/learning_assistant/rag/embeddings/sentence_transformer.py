"""SentenceTransformer embedding provider — wraps sentence-transformers."""

from learning_assistant.rag.embeddings.base import EmbeddingProvider
from learning_assistant.rag.exceptions import EmbeddingError


class SentenceTransformerEmbedding(EmbeddingProvider):
    """Embedding provider using sentence-transformers models."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(model_name)
        except ImportError as e:
            raise EmbeddingError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            ) from e
        self._model_name = model_name

    @property
    def dimension(self) -> int:
        result: int = self._model.get_sentence_embedding_dimension()
        return result

    async def embed_query(self, text: str) -> list[float]:
        return self._encode([text])[0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts)

    def _encode(self, texts: list[str]) -> list[list[float]]:
        try:
            embeddings = self._model.encode(texts, show_progress_bar=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            raise EmbeddingError(f"Encoding failed: {e}") from e
