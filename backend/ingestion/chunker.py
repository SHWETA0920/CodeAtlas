"""
Code-aware chunker using Tree-sitter.
Splits source files by top-level functions, classes, and methods.
Falls back to line-based splitting for unsupported languages.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from config import MAX_CHUNK_TOKENS

# Tree-sitter is optional — graceful fallback if not installed or parser unavailable
try:
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript
    from tree_sitter import Language, Parser

    PY_LANGUAGE = Language(tspython.language())
    JS_LANGUAGE = Language(tsjavascript.language())

    LANGUAGE_MAP = {
        "python":     PY_LANGUAGE,
        "javascript": JS_LANGUAGE,
        "typescript": JS_LANGUAGE,
    }
    TREE_SITTER_AVAILABLE = True
except Exception:
    TREE_SITTER_AVAILABLE = False
    LANGUAGE_MAP = {}


@dataclass
class CodeChunk:
    content: str
    file_path: str
    language: str
    chunk_type: str    # "function" | "class" | "module" | "block"
    name: str          # function/class name if available
    start_line: int
    end_line: int

    def to_dict(self) -> dict:
        return {
            "content":    self.content,
            "file_path":  self.file_path,
            "language":   self.language,
            "chunk_type": self.chunk_type,
            "name":       self.name,
            "start_line": self.start_line,
            "end_line":   self.end_line,
        }


# ── Node types we treat as chunk boundaries per language ─────────────
CHUNK_NODE_TYPES = {
    "python": {
        "function_definition", "async_function_definition", "class_definition",
        "decorated_definition",
    },
    "javascript": {
        "function_declaration", "arrow_function", "class_declaration",
        "method_definition", "export_statement",
    },
    "typescript": {
        "function_declaration", "arrow_function", "class_declaration",
        "method_definition", "export_statement", "interface_declaration",
        "type_alias_declaration",
    },
}


def chunk_file(file_info: dict) -> list[CodeChunk]:
    """
    Main entry point. Returns a list of CodeChunk for one source file.
    """
    content  = file_info["content"]
    path     = file_info["path"]
    language = file_info["language"]

    if TREE_SITTER_AVAILABLE and language in LANGUAGE_MAP:
        chunks = _tree_sitter_chunk(content, path, language)
    else:
        chunks = _line_based_chunk(content, path, language)

    # Safety: if a chunk is huge, split it further
    result = []
    for chunk in chunks:
        if _token_estimate(chunk.content) > MAX_CHUNK_TOKENS * 2:
            result.extend(_split_large_chunk(chunk))
        else:
            result.append(chunk)
    return result


# ── Tree-sitter strategy ──────────────────────────────────────────────

def _tree_sitter_chunk(content: str, path: str, language: str) -> list[CodeChunk]:
    ts_lang = LANGUAGE_MAP[language]
    parser  = Parser(ts_lang)
    tree    = parser.parse(bytes(content, "utf-8"))
    lines   = content.splitlines()

    target_types = CHUNK_NODE_TYPES.get(language, set())
    chunks: list[CodeChunk] = []

    def visit(node):
        if node.type in target_types:
            start = node.start_point[0]
            end   = node.end_point[0]
            body  = "\n".join(lines[start:end + 1])
            name  = _extract_name(node, content)
            chunk_type = "class" if "class" in node.type else "function"
            chunks.append(CodeChunk(
                content=body, file_path=path, language=language,
                chunk_type=chunk_type, name=name,
                start_line=start + 1, end_line=end + 1,
            ))
            return  # don't recurse inside — we want top-level only
        for child in node.children:
            visit(child)

    visit(tree.root_node)

    # If nothing found (e.g. script-style file), treat entire file as one chunk
    if not chunks:
        chunks.append(CodeChunk(
            content=content, file_path=path, language=language,
            chunk_type="module", name=path,
            start_line=1, end_line=len(lines),
        ))

    return chunks


def _extract_name(node, content: str) -> str:
    for child in node.children:
        if child.type == "identifier":
            start = child.start_byte
            end   = child.end_byte
            return content[start:end]
    return "anonymous"


# ── Regex / line-based fallback ───────────────────────────────────────

_FUNC_PATTERNS = [
    re.compile(r"^(def |async def )", re.MULTILINE),           # Python
    re.compile(r"^(function |const \w+ = (\(|async))", re.MULTILINE),  # JS
    re.compile(r"^(public |private |protected |static )", re.MULTILINE),  # Java/C#
]


def _line_based_chunk(content: str, path: str, language: str) -> list[CodeChunk]:
    lines = content.splitlines()
    split_points = {0}

    for pattern in _FUNC_PATTERNS:
        for m in pattern.finditer(content):
            line_no = content[:m.start()].count("\n")
            split_points.add(line_no)

    split_points = sorted(split_points)
    chunks = []
    for i, start in enumerate(split_points):
        end = split_points[i + 1] if i + 1 < len(split_points) else len(lines)
        body = "\n".join(lines[start:end])
        if body.strip():
            chunks.append(CodeChunk(
                content=body, file_path=path, language=language,
                chunk_type="block", name=f"block_{i}",
                start_line=start + 1, end_line=end,
            ))

    if not chunks:
        chunks.append(CodeChunk(
            content=content, file_path=path, language=language,
            chunk_type="module", name=path,
            start_line=1, end_line=len(lines),
        ))
    return chunks


# ── Helpers ───────────────────────────────────────────────────────────

def _token_estimate(text: str) -> int:
    """Rough estimate: 1 token ≈ 4 chars."""
    return len(text) // 4


def _split_large_chunk(chunk: CodeChunk) -> list[CodeChunk]:
    lines = chunk.content.splitlines()
    step  = MAX_CHUNK_TOKENS * 3  # chars per sub-chunk
    result = []
    for i in range(0, len(lines), 60):
        sub_lines = lines[i:i + 60]
        body = "\n".join(sub_lines)
        result.append(CodeChunk(
            content=body, file_path=chunk.file_path, language=chunk.language,
            chunk_type=chunk.chunk_type, name=f"{chunk.name}_part{i//60}",
            start_line=chunk.start_line + i,
            end_line=chunk.start_line + i + len(sub_lines) - 1,
        ))
    return result or [chunk]
