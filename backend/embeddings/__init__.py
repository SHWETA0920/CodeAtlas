"""Unified embedder — picks provider based on config."""
from config import EMBEDDING_PROVIDER


def get_embedder():
    if EMBEDDING_PROVIDER == "huggingface":
        from embeddings.hf_embedder import embed_texts, embed_query, get_dimension
    else:
        from embeddings.openai_embedder import embed_texts, embed_query, get_dimension

    class _Embedder:
        def embed(self, texts): return embed_texts(texts)
        def embed_one(self, text): return embed_query(text)
        def dim(self): return get_dimension()

    return _Embedder()
