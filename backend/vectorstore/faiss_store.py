"""
FAISS vector store with JSON metadata sidecar.
Each index is scoped to a project_id so multiple repos can coexist.
"""
from __future__ import annotations
import os
import json
import numpy as np
from config import FAISS_INDEX_DIR

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


def _index_path(project_id: str) -> str:
    return os.path.join(FAISS_INDEX_DIR, f"{project_id}.index")


def _meta_path(project_id: str) -> str:
    return os.path.join(FAISS_INDEX_DIR, f"{project_id}.meta.json")


def build_index(project_id: str, embeddings: list[list[float]], metadatas: list[dict]) -> None:
    """Build and persist a FAISS flat-L2 index."""
    if not FAISS_AVAILABLE:
        raise RuntimeError("faiss-cpu is not installed")

    dim = len(embeddings[0])
    vecs = np.array(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(dim)   # inner-product (cosine if normalised)
    faiss.normalize_L2(vecs)
    index.add(vecs)

    faiss.write_index(index, _index_path(project_id))
    with open(_meta_path(project_id), "w") as f:
        json.dump(metadatas, f)


def search(project_id: str, query_vec: list[float], top_k: int = 8,
           filter_language: str | None = None,
           filter_module: str | None = None) -> list[dict]:
    """
    Search the FAISS index for a project.
    Returns list of metadata dicts with an extra 'score' key.
    """
    if not FAISS_AVAILABLE:
        raise RuntimeError("faiss-cpu is not installed")

    idx_path  = _index_path(project_id)
    meta_path = _meta_path(project_id)

    if not os.path.exists(idx_path):
        raise FileNotFoundError(f"No index found for project '{project_id}'")

    index = faiss.read_index(idx_path)
    with open(meta_path) as f:
        metadatas: list[dict] = json.load(f)

    vec = np.array([query_vec], dtype="float32")
    faiss.normalize_L2(vec)

    scores, idxs = index.search(vec, min(top_k * 3, index.ntotal))

    results = []
    for score, i in zip(scores[0], idxs[0]):
        if i < 0:
            continue
        meta = dict(metadatas[i])
        meta["score"] = float(score)

        # Optional metadata filters
        if filter_language and meta.get("language") != filter_language:
            continue
        if filter_module and filter_module.lower() not in meta.get("file_path", "").lower():
            continue

        results.append(meta)
        if len(results) >= top_k:
            break

    return results


def project_exists(project_id: str) -> bool:
    return os.path.exists(_index_path(project_id))


def delete_index(project_id: str) -> None:
    for path in [_index_path(project_id), _meta_path(project_id)]:
        if os.path.exists(path):
            os.remove(path)
