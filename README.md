# DevBrain AI 🧠

> AI-powered codebase intelligence. Drop any GitHub repo or project files — ask questions, debug, and understand the entire codebase instantly.

---

## How it works

1. **Input** — GitHub URL or uploaded files
2. **Parse** — Tree-sitter extracts functions/classes/modules as chunks
3. **Embed** — OpenAI or HuggingFace converts chunks to vectors
4. **Store** — FAISS (local) or pgvector (production)
5. **Retrieve** — Multi-query expansion + similarity search + reranking
6. **Generate** — GPT-4o or Groq produces a grounded answer with file references

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |
| Git | any | system package manager |
| Docker (optional) | 24+ | [docker.com](https://docker.com) |

You also need **at least one API key**:
- **OpenAI** (recommended): https://platform.openai.com/api-keys
- **Groq** (free, fast): https://console.groq.com

---

## Quick Start (Local, No Docker)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/devbrain-ai.git
cd devbrain-ai
```

### 2. Set up the backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `.env` and add your API key:

```env
OPENAI_API_KEY=sk-...        # your OpenAI key
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
VECTOR_STORE=faiss            # faiss for local, no DB needed
```

Start the backend:

```bash
python app.py
# Flask running on http://localhost:5000
```

### 3. Set up the frontend

Open a new terminal:

```bash
cd frontend

npm install

cp .env.local.example .env.local
# BACKEND_URL=http://localhost:5000   (already set)

npm run dev
# Next.js running on http://localhost:3000
```

### 4. Open the app

Go to **http://localhost:3000**, paste a GitHub URL, and start asking questions.

---

## Docker Setup (Recommended for Production)

Docker runs everything (backend + frontend + PostgreSQL/pgvector) in one command.

### 1. Create a root `.env` file

```bash
cp backend/.env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
EMBEDDING_PROVIDER=openai
VECTOR_STORE=pgvector          # use pgvector with Docker
```

### 2. Start all services

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- PostgreSQL: localhost:5432

### 3. Stop services

```bash
docker compose down            # stop
docker compose down -v         # stop + delete database
```

---

## Using Groq (Free, Faster)

Groq provides free LLM inference (Llama 3). Get a key at https://console.groq.com

```env
LLM_PROVIDER=groq
LLM_MODEL=llama3-70b-8192
GROQ_API_KEY=gsk_...
EMBEDDING_PROVIDER=openai      # Groq doesn't provide embeddings, keep OpenAI here
```

Or use fully local/free with HuggingFace embeddings:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
EMBEDDING_PROVIDER=huggingface
HF_EMBED_MODEL=microsoft/codebert-base
```

> Note: HuggingFace models download on first run (~400MB for CodeBERT). Subsequent runs are fast.

---

## Configuration Reference

All config is in `backend/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | `openai` or `groq` |
| `LLM_MODEL` | `gpt-4o` | Model name |
| `OPENAI_API_KEY` | — | Required for OpenAI |
| `GROQ_API_KEY` | — | Required for Groq |
| `EMBEDDING_PROVIDER` | `openai` | `openai` or `huggingface` |
| `OPENAI_EMBED_MODEL` | `text-embedding-3-small` | OpenAI embed model |
| `HF_EMBED_MODEL` | `microsoft/codebert-base` | HF model name |
| `VECTOR_STORE` | `faiss` | `faiss` or `pgvector` |
| `FAISS_INDEX_DIR` | `./faiss_indexes` | Where FAISS stores indexes |
| `TOP_K` | `8` | Chunks retrieved per query |
| `MULTI_QUERY_COUNT` | `4` | Query expansion variants |
| `USE_RERANKER` | `false` | Enable cross-encoder reranker |
| `MAX_CHUNK_TOKENS` | `400` | Max tokens per chunk |

---

## API Reference

### POST /api/ingest
Index a GitHub repo:
```json
{ "github_url": "https://github.com/user/repo" }
```
Upload files: `multipart/form-data` with `files[]` field.

Response: `{ "project_id": "user_repo", "status": "processing" }`

### GET /api/ingest/status/:project_id
Poll indexing progress:
```json
{ "status": "ready", "files": 42, "chunks": 387, "message": "Indexing complete" }
```

### POST /api/query
```json
{
  "project_id": "user_repo",
  "query": "Where is authentication handled?",
  "stream": true,
  "filter_language": "python",
  "filter_module": "auth"
}
```
Streaming: Server-Sent Events with `{ type: "token", content: "..." }` and `{ type: "sources", sources: [...] }`.

---

## Upgrading FAISS → pgvector

When you're ready for production:

1. Set `VECTOR_STORE=pgvector` in `.env`
2. Start PostgreSQL (via Docker or managed DB)
3. Set `PG_HOST`, `PG_USER`, `PG_PASSWORD`, `PG_DB`
4. Re-index your projects (pgvector schema is created automatically)

---

## Project Structure

```
devbrain-ai/
├── backend/
│   ├── app.py                 # Flask entry point
│   ├── config.py              # All config from .env
│   ├── ingestion/
│   │   ├── github_loader.py   # Clone repos
│   │   ├── file_loader.py     # Handle uploads
│   │   ├── file_filter.py     # Ignore noise files
│   │   └── chunker.py         # Tree-sitter code chunking
│   ├── embeddings/
│   │   ├── openai_embedder.py
│   │   └── hf_embedder.py
│   ├── vectorstore/
│   │   ├── faiss_store.py
│   │   └── pgvector_store.py
│   ├── retrieval/
│   │   ├── retriever.py       # Main RAG pipeline
│   │   ├── multi_query.py     # Query expansion
│   │   ├── context_stitcher.py
│   │   └── reranker.py
│   ├── llm/
│   │   ├── prompt_builder.py
│   │   └── llm_chain.py       # OpenAI + Groq + streaming
│   └── api/
│       ├── ingest_routes.py
│       └── query_routes.py
└── frontend/
    ├── app/
    │   ├── page.tsx            # Landing page
    │   └── chat/page.tsx       # Chat interface
    ├── components/
    │   ├── ChatInterface.tsx
    │   └── SourceFiles.tsx
    └── lib/api.ts              # Typed API client
```

---

## Troubleshooting

**`tree-sitter` install fails on Windows**
```bash
pip install tree-sitter --no-build-isolation
```

**`faiss-cpu` not found**
```bash
pip install faiss-cpu --no-cache-dir
```

**CORS errors**
Make sure `BACKEND_URL` in `.env.local` points to where Flask is running.

**Groq rate limit**
Groq free tier has per-minute limits. Reduce `MULTI_QUERY_COUNT` to `2` to make fewer LLM calls.

**Re-index a project**
Projects are cached by project ID. To force re-index, delete the FAISS file:
```bash
rm backend/faiss_indexes/user_repo.*
```
Or in pgvector: the ingest endpoint auto-deletes and rebuilds.
