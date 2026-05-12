"""
Query API endpoint — supports both regular and streaming responses.
"""
from __future__ import annotations
import json
from flask import Blueprint, request, jsonify, Response, stream_with_context
from retrieval.retriever import retrieve
from llm.llm_chain import generate, generate_stream
from vectorstore import project_exists

query_bp = Blueprint("query", __name__)


@query_bp.post("/query")
def query():
    """
    Body: {
        "project_id": "...",
        "query": "Where is auth handled?",
        "stream": true,                  // optional, default false
        "filter_language": "python",     // optional
        "filter_module": "auth"          // optional
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    project_id = data.get("project_id", "").strip()
    query_text = data.get("query", "").strip()
    stream     = data.get("stream", False)
    filter_lang   = data.get("filter_language") or None
    filter_module = data.get("filter_module") or None

    if not project_id:
        return jsonify({"error": "project_id is required"}), 400
    if not query_text:
        return jsonify({"error": "query is required"}), 400
    if not project_exists(project_id):
        return jsonify({"error": f"Project '{project_id}' not found or not indexed yet"}), 404

    # Retrieve context
    context, sources = retrieve(
        project_id, query_text,
        filter_language=filter_lang,
        filter_module=filter_module,
    )

    if not context.strip():
        return jsonify({
            "answer":  "I couldn't find relevant code for that query. "
                       "Try rephrasing or check the project was indexed correctly.",
            "sources": [],
        })

    # ── Streaming ─────────────────────────────────────────────────────
    if stream:
        def event_stream():
            # First chunk: send sources metadata
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

            # Stream LLM tokens
            for token in generate_stream(query_text, context):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            yield "data: [DONE]\n\n"

        return Response(
            stream_with_context(event_stream()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # ── Non-streaming ─────────────────────────────────────────────────
    answer = generate(query_text, context)
    return jsonify({"answer": answer, "sources": sources})
