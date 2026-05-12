"""Clone a GitHub repo into a temp directory and return all source file paths."""
import os
import tempfile
import shutil
from typing import Generator
from git import Repo
from ingestion.file_filter import is_ignored


def clone_repo(github_url: str) -> tuple[str, list[dict]]:
    """
    Clone repo to a temp dir.
    Returns (temp_dir_path, list of {path, language, content}).
    Caller is responsible for deleting temp_dir when done.
    """
    tmp = tempfile.mkdtemp(prefix="devbrain_")
    try:
        Repo.clone_from(github_url, tmp, depth=1)
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise ValueError(f"Failed to clone repo: {e}") from e

    files = list(_collect_files(tmp))
    return tmp, files


def _collect_files(root: str) -> Generator[dict, None, None]:
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in-place so os.walk skips them
        dirnames[:] = [
            d for d in dirnames
            if not is_ignored(os.path.join(dirpath, d), is_dir=True)
        ]
        for filename in filenames:
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, root)
            if is_ignored(abs_path, is_dir=False):
                continue
            lang = detect_language(filename)
            if lang is None:
                continue
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if content.strip():
                    yield {"path": rel_path, "language": lang, "content": content}
            except Exception:
                continue


def detect_language(filename: str) -> str | None:
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".jsx": "javascript", ".tsx": "typescript", ".cpp": "cpp",
        ".cc": "cpp", ".c": "c", ".h": "c", ".hpp": "cpp",
        ".go": "go", ".rs": "rust", ".java": "java", ".rb": "ruby",
        ".php": "php", ".cs": "csharp", ".swift": "swift",
        ".kt": "kotlin", ".md": "markdown", ".json": "json",
        ".yaml": "yaml", ".yml": "yaml", ".env.example": "env",
        ".sh": "bash", ".sql": "sql",
    }
    _, ext = os.path.splitext(filename.lower())
    return ext_map.get(ext)
