"""Optional cross-encoder reranker to filter retrieved chunks."""
from __future__ import annotations
from config import USE_RERANKER, RERANKER_MODEL

_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def rerank(query: str, chunks: list[dict], top_k: int = 8) -> list[dict]:
    """
    Rerank chunks using a cross-encoder model.
    Only active when USE_RERANKER=true in config.
    """
    if not USE_RERANKER or not chunks:
        return chunks[:top_k]

    try:
        model = _get_reranker()
        pairs = [(query, chunk.get("content", "")) for chunk in chunks]
        scores = model.predict(pairs)

        for chunk, score in zip(chunks, scores):
            chunk["rerank_score"] = float(score)

        reranked = sorted(chunks, key=lambda c: c.get("rerank_score", 0), reverse=True)
        return reranked[:top_k]

    except Exception:
        return chunks[:top_k]
