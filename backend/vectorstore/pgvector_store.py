"""
pgvector store for production deployments.
Requires PostgreSQL + pgvector extension.
"""
from __future__ import annotations
import json
import uuid
from sqlalchemy import create_engine, text, Column, String, JSON, Integer
from sqlalchemy.orm import declarative_base, Session
from pgvector.sqlalchemy import Vector
from config import PG_URL

Base = declarative_base()
_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(PG_URL, pool_pre_ping=True)
        _init_schema()
    return _engine


def _init_schema():
    engine = create_engine(PG_URL)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS code_chunks (
                id          TEXT PRIMARY KEY,
                project_id  TEXT NOT NULL,
                content     TEXT NOT NULL,
                file_path   TEXT,
                language    TEXT,
                chunk_type  TEXT,
                name        TEXT,
                start_line  INTEGER,
                end_line    INTEGER,
                embedding   vector(1536)
            )
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_chunks_project
            ON code_chunks (project_id)
        """))
        conn.commit()


def upsert_chunks(project_id: str, chunks: list[dict], embeddings: list[list[float]]) -> None:
    engine = _get_engine()
    with Session(engine) as session:
        # Delete old chunks for this project
        session.execute(text("DELETE FROM code_chunks WHERE project_id = :pid"),
                        {"pid": project_id})
        session.commit()

        for chunk, emb in zip(chunks, embeddings):
            session.execute(text("""
                INSERT INTO code_chunks
                    (id, project_id, content, file_path, language, chunk_type,
                     name, start_line, end_line, embedding)
                VALUES
                    (:id, :project_id, :content, :file_path, :language,
                     :chunk_type, :name, :start_line, :end_line, :embedding)
            """), {
                "id":         str(uuid.uuid4()),
                "project_id": project_id,
                "content":    chunk["content"],
                "file_path":  chunk.get("file_path", ""),
                "language":   chunk.get("language", ""),
                "chunk_type": chunk.get("chunk_type", "block"),
                "name":       chunk.get("name", ""),
                "start_line": chunk.get("start_line", 0),
                "end_line":   chunk.get("end_line", 0),
                "embedding":  json.dumps(emb),
            })
        session.commit()


def search(project_id: str, query_vec: list[float], top_k: int = 8,
           filter_language: str | None = None,
           filter_module: str | None = None) -> list[dict]:

    engine = _get_engine()
    conditions = ["project_id = :pid"]
    params: dict = {"pid": project_id, "topk": top_k,
                    "qvec": json.dumps(query_vec)}

    if filter_language:
        conditions.append("language = :lang")
        params["lang"] = filter_language
    if filter_module:
        conditions.append("file_path ILIKE :mod")
        params["mod"] = f"%{filter_module}%"

    where = " AND ".join(conditions)
    sql = text(f"""
        SELECT content, file_path, language, chunk_type, name,
               start_line, end_line,
               1 - (embedding <=> cast(:qvec as vector)) AS score
        FROM code_chunks
        WHERE {where}
        ORDER BY embedding <=> cast(:qvec as vector)
        LIMIT :topk
    """)

    with Session(engine) as session:
        rows = session.execute(sql, params).fetchall()

    return [
        {
            "content":    r.content,
            "file_path":  r.file_path,
            "language":   r.language,
            "chunk_type": r.chunk_type,
            "name":       r.name,
            "start_line": r.start_line,
            "end_line":   r.end_line,
            "score":      float(r.score),
        }
        for r in rows
    ]


def project_exists(project_id: str) -> bool:
    engine = _get_engine()
    with Session(engine) as session:
        row = session.execute(
            text("SELECT 1 FROM code_chunks WHERE project_id=:pid LIMIT 1"),
            {"pid": project_id}
        ).fetchone()
        return row is not None
