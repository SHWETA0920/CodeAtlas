"""Handle user-uploaded project files (zip archive or individual files)."""
import os
import zipfile
import tempfile
import shutil
from ingestion.github_loader import _collect_files


def load_uploaded_files(upload_dir: str, filenames: list[str]) -> tuple[str, list[dict]]:
    """
    Given an upload directory containing uploaded files, extract and collect
    all source files. Supports a single .zip or multiple flat files.
    Returns (work_dir, list of {path, language, content}).
    Caller deletes work_dir when done.
    """
    work_dir = tempfile.mkdtemp(prefix="devbrain_upload_")

    for fname in filenames:
        src = os.path.join(upload_dir, fname)
        if fname.lower().endswith(".zip"):
            _extract_zip(src, work_dir)
        else:
            dst = os.path.join(work_dir, fname)
            shutil.copy2(src, dst)

    files = list(_collect_files(work_dir))
    return work_dir, files


def _extract_zip(zip_path: str, dest_dir: str) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            # Security: prevent path traversal
            member_path = os.path.realpath(os.path.join(dest_dir, member.filename))
            if not member_path.startswith(os.path.realpath(dest_dir)):
                continue
            zf.extract(member, dest_dir)
