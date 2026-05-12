"""HuggingFace sentence-transformers embedder (local, private)."""
from __future__ import annotations
from config import HF_EMBED_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(HF_EMBED_MODEL)
    return _model


def embed_texts(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    model = _get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


def get_dimension() -> int:
    model = _get_model()
    return model.get_sentence_embedding_dimension()
