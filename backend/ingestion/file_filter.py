"""Filter out directories and files that should not be indexed."""
import os

IGNORED_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", "dist", "build",
    "out", ".cache", "coverage", ".nyc_output", "venv", ".venv",
    "env", ".env", "target", ".idea", ".vscode", ".DS_Store",
    "vendor", "bower_components", ".pytest_cache", "eggs",
    ".eggs", "htmlcov", ".tox", "site-packages",
}

IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".mp4", ".mp3", ".wav", ".pdf", ".zip", ".tar", ".gz",
    ".lock", ".sum", ".min.js", ".min.css", ".map",
    ".pyc", ".pyo", ".class", ".o", ".so", ".dylib", ".dll",
    ".exe", ".wasm", ".bin",
}

IGNORED_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "Cargo.lock", "poetry.lock", "Pipfile.lock",
    ".gitignore", ".eslintignore", ".prettierignore",
    "LICENSE", "LICENCE",
}

MAX_FILE_SIZE_BYTES = 500_000  # 500 KB


def is_ignored(path: str, is_dir: bool) -> bool:
    name = os.path.basename(path)

    if is_dir:
        return name in IGNORED_DIRS or name.startswith(".")

    if name in IGNORED_FILES:
        return True

    _, ext = os.path.splitext(name.lower())
    if ext in IGNORED_EXTENSIONS:
        return True

    # Skip minified files (heuristic: very long lines)
    try:
        size = os.path.getsize(path)
        if size > MAX_FILE_SIZE_BYTES:
            return True
    except OSError:
        return True

    return False
