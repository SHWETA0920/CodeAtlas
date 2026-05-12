"""
Main retriever: multi-query expansion → vector search → reranking → context stitch.
"""
from __future__ import annotations
from embeddings import get_embedder
from vectorstore import search
from retrieval.multi_query import expand_query
from retrieval.context_stitcher import stitch_context
from retrieval.reranker import rerank
from config import TOP_K


def retrieve(
    project_id: str,
    query: str,
    top_k: int = TOP_K,
    filter_language: str | None = None,
    filter_module: str | None = None,
    use_multi_query: bool = True,
) -> tuple[str, list[dict]]:
    """
    Full RAG retrieval pipeline.
    Returns (context_string, source_references).
    """
    embedder = get_embedder()

    # 1. Expand query into multiple variants
    queries = expand_query(query) if use_multi_query else [query]

    # 2. Retrieve chunks for each query variant
    seen_keys: set[tuple] = set()
    all_chunks: list[dict] = []

    for q in queries:
        vec = embedder.embed_one(q)
        chunks = search(
            project_id, vec,
            top_k=top_k,
            filter_language=filter_language,
            filter_module=filter_module,
        )
        for chunk in chunks:
            key = (chunk.get("file_path", ""), chunk.get("start_line", 0))
            if key not in seen_keys:
                seen_keys.add(key)
                all_chunks.append(chunk)

    # 3. Rerank if enabled
    all_chunks = rerank(query, all_chunks, top_k=top_k * 2)

    # 4. Stitch into final context
    context, sources = stitch_context(all_chunks)
    return context, sources
