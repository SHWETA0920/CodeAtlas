"""
Context Stitcher: deduplicate and merge retrieved chunks from multiple
files into a coherent context string for the LLM.
"""
from __future__ import annotations


def stitch_context(chunks: list[dict], max_chars: int = 12000) -> tuple[str, list[dict]]:
    """
    Merge chunks into a single context string.
    Returns (context_string, list_of_source_references).
    """
    # Deduplicate by (file_path, start_line)
    seen: set[tuple] = set()
    unique: list[dict] = []
    for chunk in chunks:
        key = (chunk.get("file_path", ""), chunk.get("start_line", 0))
        if key not in seen:
            seen.add(key)
            unique.append(chunk)

    # Sort: higher score first
    unique.sort(key=lambda c: c.get("score", 0), reverse=True)

    parts: list[str] = []
    sources: list[dict] = []
    total_chars = 0

    for chunk in unique:
        header = (
            f"### File: {chunk.get('file_path', 'unknown')} "
            f"[{chunk.get('language', '')}] "
            f"({chunk.get('chunk_type', 'block')}: {chunk.get('name', '')} "
            f"lines {chunk.get('start_line', '?')}–{chunk.get('end_line', '?')})"
        )
        body = chunk.get("content", "")
        block = f"{header}\n```{chunk.get('language', '')}\n{body}\n```\n"

        if total_chars + len(block) > max_chars:
            break

        parts.append(block)
        total_chars += len(block)
        sources.append({
            "file_path":  chunk.get("file_path", ""),
            "language":   chunk.get("language", ""),
            "chunk_type": chunk.get("chunk_type", ""),
            "name":       chunk.get("name", ""),
            "start_line": chunk.get("start_line"),
            "end_line":   chunk.get("end_line"),
            "score":      round(chunk.get("score", 0), 4),
        })

    context = "\n".join(parts)
    return context, sources
