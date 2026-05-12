from config import VECTOR_STORE

if VECTOR_STORE == "pgvector":
    from vectorstore.pgvector_store import (
        upsert_chunks as _upsert,
        search        as _search,
        project_exists as _exists,
    )
    def build_index(project_id, embeddings, metadatas):
        _upsert(project_id, metadatas, embeddings)
else:
    from vectorstore.faiss_store import (
        build_index    as _build,
        search         as _search,
        project_exists as _exists,
    )
    def build_index(project_id, embeddings, metadatas):
        _build(project_id, embeddings, metadatas)


def search(project_id, query_vec, top_k=8,
           filter_language=None, filter_module=None):
    return _search(project_id, query_vec, top_k,
                   filter_language=filter_language,
                   filter_module=filter_module)


def project_exists(project_id):
    return _exists(project_id)
