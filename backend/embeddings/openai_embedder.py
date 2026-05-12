"""OpenAI text-embedding-3-small embedder."""
from __future__ import annotations
import time
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_EMBED_MODEL

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def embed_texts(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """
    Embed a list of texts in batches.
    Returns list of float vectors.
    """
    client = _get_client()
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        for attempt in range(3):
            try:
                response = client.embeddings.create(
                    model=OPENAI_EMBED_MODEL,
                    input=batch,
                )
                all_embeddings.extend([item.embedding for item in response.data])
                break
            except Exception as e:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)

    return all_embeddings


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


def get_dimension() -> int:
    """Return embedding vector dimension for text-embedding-3-small."""
    return 1536
