"""
Ingest API endpoint.
Accepts a GitHub URL or uploaded files, indexes the codebase,
and returns a project_id.
"""
from __future__ import annotations
import os
import shutil
import hashlib
import threading
from flask import Blueprint, request, jsonify
from config import UPLOAD_DIR
from ingestion.github_loader import clone_repo
from ingestion.file_loader import load_uploaded_files
from ingestion.chunker import chunk_file
from embeddings import get_embedder
from vectorstore import build_index, project_exists

ingest_bp = Blueprint("ingest", __name__)

# Track background ingestion jobs
_jobs: dict[str, dict] = {}


@ingest_bp.post("/ingest")
def ingest():
    """
    Body (JSON):  { "github_url": "https://github.com/..." }
    Body (form):  multipart/form-data with files[] field
    Returns: { "project_id": "...", "status": "processing" }
    """
    # ── GitHub URL ingestion ──────────────────────────────────────────
    if request.is_json:
        data = request.get_json()
        github_url = data.get("github_url", "").strip()
        if not github_url:
            return jsonify({"error": "github_url is required"}), 400

        project_id = _url_to_project_id(github_url)
        if project_exists(project_id):
            return jsonify({"project_id": project_id, "status": "ready",
                            "message": "Already indexed"}), 200

        _start_job(project_id, source="github", github_url=github_url)
        return jsonify({"project_id": project_id, "status": "processing"}), 202

    # ── File upload ingestion ─────────────────────────────────────────
    files = request.files.getlist("files[]")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    project_id = _generate_upload_project_id(files)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved = []
    for f in files:
        dest = os.path.join(UPLOAD_DIR, f.filename)
        f.save(dest)
        saved.append(f.filename)

    _start_job(project_id, source="upload",
               upload_dir=UPLOAD_DIR, filenames=saved)
    return jsonify({"project_id": project_id, "status": "processing"}), 202


@ingest_bp.get("/ingest/status/<project_id>")
def ingest_status(project_id: str):
    """Poll ingestion status."""
    if project_id not in _jobs:
        if project_exists(project_id):
            return jsonify({"project_id": project_id, "status": "ready"})
        return jsonify({"error": "Unknown project"}), 404

    job = _jobs[project_id]
    return jsonify({
        "project_id": project_id,
        "status":     job["status"],
        "message":    job.get("message", ""),
        "chunks":     job.get("chunks", 0),
        "files":      job.get("files", 0),
    })


# ── Background worker ─────────────────────────────────────────────────

def _start_job(project_id: str, **kwargs):
    _jobs[project_id] = {"status": "processing", "chunks": 0, "files": 0}
    t = threading.Thread(target=_run_ingestion, args=(project_id,),
                         kwargs=kwargs, daemon=True)
    t.start()


def _run_ingestion(project_id: str, source: str = "github", **kwargs):
    tmp_dir = None
    try:
        _jobs[project_id]["message"] = "Fetching files..."

        if source == "github":
            tmp_dir, file_infos = clone_repo(kwargs["github_url"])
        else:
            tmp_dir, file_infos = load_uploaded_files(
                kwargs["upload_dir"], kwargs["filenames"]
            )

        _jobs[project_id]["files"] = len(file_infos)
        _jobs[project_id]["message"] = f"Parsing {len(file_infos)} files..."

        # Chunk all files
        all_chunks = []
        for fi in file_infos:
            all_chunks.extend(chunk_file(fi))

        _jobs[project_id]["chunks"] = len(all_chunks)
        _jobs[project_id]["message"] = f"Embedding {len(all_chunks)} chunks..."

        # Embed
        embedder = get_embedder()
        texts = [c.content for c in all_chunks]
        embeddings = embedder.embed(texts)

        _jobs[project_id]["message"] = "Building index..."
        metadatas = [c.to_dict() for c in all_chunks]
        build_index(project_id, embeddings, metadatas)

        _jobs[project_id]["status"]  = "ready"
        _jobs[project_id]["message"] = "Indexing complete"

    except Exception as e:
        _jobs[project_id]["status"]  = "error"
        _jobs[project_id]["message"] = str(e)
    finally:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)


# ── Helpers ───────────────────────────────────────────────────────────

def _url_to_project_id(url: str) -> str:
    clean = url.rstrip("/").lower()
    # e.g. "github.com/user/repo" → "user_repo"
    parts = clean.split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}_{parts[-1]}"[:64]
    return hashlib.md5(clean.encode()).hexdigest()[:16]


def _generate_upload_project_id(files) -> str:
    names = sorted(f.filename for f in files)
    return "upload_" + hashlib.md5(",".join(names).encode()).hexdigest()[:12]
