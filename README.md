# CodeAtlas 🧠

> **AI-powered codebase intelligence.** Drop any GitHub repo or upload project files — ask questions, debug, and understand the entire codebase instantly like a senior developer who has read every single file.

<br/>

![CodeAtlas](https://img.shields.io/badge/DevBrain-AI%20Powered-6366f1?style=for-the-badge&logo=brain&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG-1c3c3c?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📋 Table of Contents

- [What is CodeAtlas ?](#-what-is-devbrain-ai)
- [How It Works](#-how-it-works)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
  - [Local Setup (No Docker)](#option-a--local-setup-no-docker)
  - [Docker Setup](#option-b--docker-setup)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Free API Providers](#-free-api-providers)
- [Usage Guide](#-usage-guide)
- [Troubleshooting](#-troubleshooting)
- [Performance Tips](#-performance-tips)
- [Roadmap](#-roadmap)

---

## 🤔 What is CodeAtlas?

Every developer knows the pain of:
- Joining a new project and spending days just understanding the codebase
- Searching `Ctrl+F` across 50 files to find where a feature is implemented
- Debugging an issue that spans 5 different files across 3 modules
- Trying to understand why a function exists and what it connects to

**CodeAtlas solves all of this.**

You give it a GitHub repo URL or upload your project files. It reads, parses, and indexes the entire codebase using RAG (Retrieval-Augmented Generation). Then you can ask it anything in plain English — and it answers with full context, file references, and code snippets.

```
You:  "Where is user authentication handled and how does JWT work here?"

DevBrain: Authentication is handled across 3 files:
          → auth/middleware.py (lines 12–67): JWT verification logic
          → routes/auth_routes.py (lines 23–89): login/logout endpoints  
          → models/user.py (lines 5–34): User model with password hashing
          
          The JWT token is generated in login_user() using PyJWT with a 
          24-hour expiry. The middleware validates it on every protected route...
```

---

## ⚙️ How It Works

DevBrain AI uses a **RAG (Retrieval-Augmented Generation)** pipeline with code-aware chunking:

```
User Input (GitHub URL / Files)
         ↓
   Code Parsing
   (Tree-sitter splits by functions, classes, modules)
         ↓
   Embedding Generation
   (HuggingFace all-MiniLM-L6-v2 → vectors)
         ↓
   Vector Storage
   (FAISS local index with metadata)
         ↓
   User Query
         ↓
   Multi-Query Expansion
   ("auth" → ["authentication", "login", "JWT", "middleware"])
         ↓
   Similarity Search
   (Find top-K most relevant code chunks)
         ↓
   Context Stitching
   (Merge chunks from multiple files)
         ↓
   LLM Response
   (Groq/OpenAI generates grounded answer)
         ↓
   Answer + Source References
```

### Why Code-Aware Chunking Matters

Normal RAG splits text by character count. This breaks functions in half and destroys context.

DevBrain uses **Tree-sitter** to split by actual code structure:

```python
# ❌ Normal chunking (bad)
"...def login_user(username, pas"   ← chunk boundary mid-function
"sword):\n    user = db.query..."

# ✅ CodeAtlas chunking (good)
"def login_user(username, password):    ← entire function = one chunk
    user = db.query(User).filter(...)
    if not verify_password(...):
        raise AuthError(...)
    return generate_jwt(user.id)"
```

This means every chunk is a complete, meaningful unit of code — which massively improves retrieval accuracy.

---

## ✨ Features

### Core Features
- **🔍 Smart Code Search** — Finds code by meaning, not just keywords. "Where is rate limiting?" finds it even if the variable is named `throttle_requests`
- **🧠 Architecture Explainer** — Ask "explain the project structure" and get a full breakdown of modules, dependencies, and data flow
- **🐛 Debugging Assistant** — "Why is login failing?" traces through auth middleware, database queries, and error handling across all relevant files
- **⚡ Code Optimizer** — Ask to optimize a function and get suggestions with time complexity analysis
- **📁 Multi-File Context** — Answers span multiple files simultaneously, showing exactly how code connects

### Advanced RAG Features
- **Multi-Query Expansion** — One query becomes 4 variants to maximize retrieval coverage
- **Context Stitching** — Intelligently merges relevant chunks from different files without duplication
- **Metadata Filtering** — Filter search to specific languages (`python`) or modules (`auth`)
- **Cross-Encoder Reranker** — Optional second-pass reranking for higher precision (enable with `USE_RERANKER=true`)
- **Streaming Responses** — Answers stream token-by-token like ChatGPT for instant feedback

### Developer Experience
- **Background Indexing** — Ingestion runs in a background thread with real-time progress polling
- **Project Caching** — Indexed projects are cached; re-asking questions is instant
- **Source References** — Every answer shows exactly which files and line numbers were used
- **Language Detection** — Automatically detects Python, JS, TS, Go, Rust, Java, C++, and more
- **Smart File Filtering** — Automatically ignores `node_modules`, `build`, `.git`, binary files

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Core runtime |
| Flask | 3.0.3 | REST API + SSE streaming |
| LangChain | 0.2.6 | RAG orchestration |
| Tree-sitter | 0.21.3 | Code-aware AST parsing |
| GitPython | 3.1.43 | Clone GitHub repos |

### Embeddings & Vector Store
| Technology | Purpose |
|-----------|---------|
| `sentence-transformers/all-MiniLM-L6-v2` | Free local embeddings (80MB, 384-dim) |
| `microsoft/codebert-base` | Alternative code-specific embeddings |
| `text-embedding-3-small` (OpenAI) | Cloud embeddings (paid) |
| FAISS | Local vector index (MVP) |
| pgvector | Production vector DB (PostgreSQL) |

### LLM Providers
| Provider | Models | Cost |
|---------|--------|------|
| Groq | llama3-70b, llama3-8b, mixtral-8x7b | **Free tier** |
| OpenAI | gpt-4o, gpt-3.5-turbo | Paid |
| Google Gemini | gemini-1.5-flash | Free tier |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 14.2.35 | React framework |
| TypeScript | 5+ | Type safety |
| Tailwind CSS | 3.4 | Styling |
| react-markdown | 9.0 | Render markdown answers |
| lucide-react | 0.400 | Icons |

---

## 📁 Project Structure

```
devbrain-ai/
│
├── 📄 README.md
├── 📄 docker-compose.yml          # Full stack: backend + frontend + postgres
├── 📄 .gitignore
│
├── 🐍 backend/
│   ├── app.py                     # Flask app factory, registers blueprints
│   ├── config.py                  # All config loaded from .env
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile
│   ├── .env.example               # Template — copy to .env
│   │
│   ├── ingestion/                 # Step 1-3: Input → Parse → Chunk
│   │   ├── github_loader.py       # Clone repo, walk files, detect language
│   │   ├── file_loader.py         # Handle zip uploads, extract safely
│   │   ├── file_filter.py         # Ignore node_modules, binaries, etc.
│   │   └── chunker.py             # Tree-sitter AST chunking + fallback
│   │
│   ├── embeddings/                # Step 4: Text → Vectors
│   │   ├── __init__.py            # Unified interface (picks provider)
│   │   ├── openai_embedder.py     # OpenAI text-embedding-3-small
│   │   └── hf_embedder.py         # HuggingFace sentence-transformers
│   │
│   ├── vectorstore/               # Step 5: Store & Search Vectors
│   │   ├── __init__.py            # Unified interface (faiss or pgvector)
│   │   ├── faiss_store.py         # Local FAISS flat index + JSON metadata
│   │   └── pgvector_store.py      # PostgreSQL pgvector (production)
│   │
│   ├── retrieval/                 # Step 6: Core RAG Logic
│   │   ├── retriever.py           # Main pipeline: expand→search→rerank→stitch
│   │   ├── multi_query.py         # Expand 1 query into N variants via LLM
│   │   ├── context_stitcher.py    # Deduplicate & merge chunks into context
│   │   └── reranker.py            # Optional cross-encoder reranker
│   │
│   ├── llm/                       # Step 7: Generate Response
│   │   ├── prompt_builder.py      # System prompt + context template
│   │   └── llm_chain.py           # OpenAI/Groq, streaming + non-streaming
│   │
│   ├── api/                       # Flask route handlers
│   │   ├── ingest_routes.py       # POST /api/ingest, GET /api/ingest/status
│   │   └── query_routes.py        # POST /api/query (SSE streaming)
│   │
│   └── utils/
│       ├── language_detector.py   # Map file extensions → language names
│       └── metadata_extractor.py  # Extract file path, module, function name
│
└── ⚛️ frontend/
    ├── package.json
    ├── next.config.js             # Rewrites /api/backend/* → Flask
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── Dockerfile
    ├── .env.local.example
    │
    ├── app/
    │   ├── layout.tsx             # Root layout, fonts, metadata
    │   ├── globals.css            # Tailwind base + custom styles
    │   ├── page.tsx               # Landing page: GitHub URL + file upload
    │   └── chat/
    │       └── page.tsx           # Chat interface page
    │
    ├── components/
    │   ├── ChatInterface.tsx      # Full streaming chat UI with state mgmt
    │   └── SourceFiles.tsx        # Referenced files panel with scores
    │
    └── lib/
        └── api.ts                 # Typed fetch helpers for all API calls
```

---

## 📦 Prerequisites

Before you start, install these on your machine:

### Required

**Python 3.11+**
```bash
python --version   # should show 3.11 or higher
```
Download: https://python.org/downloads
> ⚠️ Windows: check **"Add Python to PATH"** during installation

**Node.js 20+**
```bash
node --version     # should show v20 or higher
```
Download: https://nodejs.org (choose LTS)

**Git**
```bash
git --version
```
Download: https://git-scm.com/downloads

### API Keys (at least one LLM provider)

| Provider | Free? | Get Key |
|---------|-------|---------|
| **Groq** ✅ Recommended | Yes, free tier | https://console.groq.com |
| OpenAI | Paid | https://platform.openai.com/api-keys |
| Google Gemini | Free tier | https://aistudio.google.com/app/apikey |

> **HuggingFace embeddings are completely free** — no key needed, model downloads automatically.

### VS Code Extensions (Recommended)
- **Python** (Microsoft)
- **Pylance**
- **ES7+ React/Redux Snippets**
- **Tailwind CSS IntelliSense**
- **TypeScript** (built-in)

---

## 🚀 Installation & Setup

### Option A — Local Setup (No Docker)

Best for development. Fastest to get started.

#### Step 1: Get the project

```bash
# If you have the zip:
unzip codeatlas.zip
cd codeatlas

# Or clone from GitHub:
git clone https://github.com/your-username/codeatlas.git
cd codeatlas
```

#### Step 2: Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows (Command Prompt)
.\venv\Scripts\Activate.ps1     # Windows (PowerShell)

# Install dependencies (takes 3-5 minutes)
pip install -r requirements.txt
```

#### Step 3: Configure backend

```bash
cp .env.example .env
```

Open `backend/.env` and configure:

```env
# ── Minimum config to get started ────────────────────────

# Groq (free) — get key at https://console.groq.com
LLM_PROVIDER=groq
LLM_MODEL=llama3-8b-8192
GROQ_API_KEY=your_groq_api_key_here

# HuggingFace embeddings — FREE, no key needed
EMBEDDING_PROVIDER=huggingface
HF_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
SENTENCE_TRANSFORMERS_HOME=./model_cache

# FAISS — local vector store, no setup needed
VECTOR_STORE=faiss
FAISS_INDEX_DIR=./faiss_indexes

# Performance
TOP_K=5
MULTI_QUERY_COUNT=0
USE_RERANKER=false

# App
FLASK_DEBUG=true
SECRET_KEY=your_secret_key_here
UPLOAD_DIR=./uploads
```

#### Step 4: Frontend setup

Open a **new terminal** (keep backend terminal open):

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

`frontend/.env.local` should contain:
```env
BACKEND_URL=http://localhost:5000
```

#### Step 5: Run both servers

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate           # Windows
# source venv/bin/activate      # macOS/Linux
python app.py
```

Expected output:
```
* Running on http://0.0.0.0:5000
* Debug mode: on
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Expected output:
```
▲ Next.js 14.2.35
- Local: http://localhost:3000
✓ Ready in 2.1s
```

#### Step 6: Open the app

Go to **http://localhost:3000** in your browser.

To verify backend is healthy: http://127.0.0.1:5000/health
```json
{ "status": "ok", "service": "devbrain-ai" }
```

---

### Option B — Docker Setup

Best for production. Runs everything in one command including PostgreSQL.

#### Step 1: Install Docker Desktop
Download: https://docker.com/products/docker-desktop

#### Step 2: Configure environment

```bash
cd codeatlas
cp backend/.env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-...          # or use Groq:
GROQ_API_KEY=gsk_...
LLM_PROVIDER=groq
LLM_MODEL=llama3-8b-8192
EMBEDDING_PROVIDER=huggingface
VECTOR_STORE=pgvector           # use pgvector with Docker
```

#### Step 3: Start everything

```bash
docker compose up --build
```

First run downloads images and builds containers (~5 minutes).
Subsequent runs start in ~30 seconds.

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **PostgreSQL:** localhost:5432

#### Step 4: Stop

```bash
docker compose down             # stop containers
docker compose down -v          # stop + wipe database
```

---

## ⚙️ Configuration

All backend config lives in `backend/.env`. Full reference:

### LLM Settings
| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `LLM_PROVIDER` | `openai` | `openai`, `groq` | Which LLM to use |
| `LLM_MODEL` | `gpt-4o` | Any model name | Specific model |
| `OPENAI_API_KEY` | — | `sk-...` | Required for OpenAI |
| `GROQ_API_KEY` | — | `gsk_...` | Required for Groq |

**Groq model options:**
- `llama3-8b-8192` — fastest, good quality
- `llama3-70b-8192` — best quality, slower
- `mixtral-8x7b-32768` — best for long codebases (32k context)

### Embedding Settings
| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `EMBEDDING_PROVIDER` | `openai` | `openai`, `huggingface` | Embedding source |
| `OPENAI_EMBED_MODEL` | `text-embedding-3-small` | — | OpenAI model |
| `HF_EMBED_MODEL` | `microsoft/codebert-base` | Any HF model | Local model |
| `SENTENCE_TRANSFORMERS_HOME` | — | `./model_cache` | Cache directory |

**Recommended free HuggingFace models:**
- `sentence-transformers/all-MiniLM-L6-v2` — 80MB, fastest, great quality
- `microsoft/codebert-base` — 500MB, code-specific

### Vector Store Settings
| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `VECTOR_STORE` | `faiss` | `faiss`, `pgvector` | Storage backend |
| `FAISS_INDEX_DIR` | `./faiss_indexes` | Any path | FAISS save location |
| `PG_HOST` | `localhost` | — | PostgreSQL host |
| `PG_PORT` | `5432` | — | PostgreSQL port |
| `PG_USER` | `devbrain` | — | PostgreSQL user |
| `PG_PASSWORD` | `devbrain` | — | PostgreSQL password |
| `PG_DB` | `devbrain` | — | Database name |

### RAG Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `TOP_K` | `8` | Number of chunks retrieved per query |
| `MULTI_QUERY_COUNT` | `4` | Query expansion variants (0 = disabled) |
| `USE_RERANKER` | `false` | Enable cross-encoder reranking |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Reranker model |
| `MAX_CHUNK_TOKENS` | `400` | Max tokens per code chunk |

---

## 📡 API Reference

### POST /api/ingest
Index a GitHub repository or uploaded files.

**GitHub URL:**
```bash
curl -X POST http://localhost:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/user/repo"}'
```

**File upload:**
```bash
curl -X POST http://localhost:5000/api/ingest \
  -F "files[]=@myproject.zip"
```

**Response:**
```json
{
  "project_id": "user_repo",
  "status": "processing"
}
```

---

### GET /api/ingest/status/:project_id
Poll ingestion progress.

```bash
curl http://localhost:5000/api/ingest/status/user_repo
```

**Response (processing):**
```json
{
  "project_id": "user_repo",
  "status": "processing",
  "message": "Embedding 342 chunks...",
  "files": 47,
  "chunks": 342
}
```

**Response (ready):**
```json
{
  "project_id": "user_repo",
  "status": "ready",
  "message": "Indexing complete",
  "files": 47,
  "chunks": 342
}
```

---

### POST /api/query
Query the indexed codebase.

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "user_repo",
    "query": "Where is authentication handled?",
    "stream": false,
    "filter_language": "python",
    "filter_module": "auth"
  }'
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | string | ✅ | From ingest response |
| `query` | string | ✅ | Natural language question |
| `stream` | boolean | ❌ | Enable SSE streaming (default: false) |
| `filter_language` | string | ❌ | Only search this language |
| `filter_module` | string | ❌ | Only search files containing this string |

**Non-streaming response:**
```json
{
  "answer": "Authentication is handled in auth/middleware.py...",
  "sources": [
    {
      "file_path": "auth/middleware.py",
      "language": "python",
      "chunk_type": "function",
      "name": "verify_jwt_token",
      "start_line": 23,
      "end_line": 67,
      "score": 0.9241
    }
  ]
}
```

**Streaming response (SSE):**
```
data: {"type": "sources", "sources": [...]}

data: {"type": "token", "content": "Authentication"}
data: {"type": "token", "content": " is"}
data: {"type": "token", "content": " handled"}
...
data: [DONE]
```

---

### GET /health
Check if backend is running.

```bash
curl http://localhost:5000/health
```
```json
{ "status": "ok", "service": "devbrain-ai" }
```

---

## 🆓 Free API Providers

You can run DevBrain AI at **zero cost** with these free providers:

### Groq (LLM) — Recommended
- **Free tier:** 14,400 requests/day, 30 req/min
- **Get key:** https://console.groq.com
- **Best models:**
  - `llama3-8b-8192` — fast everyday use
  - `llama3-70b-8192` — complex analysis
  - `mixtral-8x7b-32768` — large codebases

### HuggingFace (Embeddings) — Completely Free
- No API key needed
- Runs entirely on your machine
- Downloads once, cached forever
- **Best model:** `sentence-transformers/all-MiniLM-L6-v2`

### Google Gemini (Alternative LLM)
- **Free tier:** 15 req/min, 1500/day
- **Get key:** https://aistudio.google.com/app/apikey

### FAISS (Vector Store) — Completely Free
- Runs locally, no server needed
- Persists to disk between restarts
- Handles codebases up to ~100k chunks easily

---

## 📖 Usage Guide

### 1. Index a Repository

On the homepage, paste any public GitHub URL:
```
https://github.com/pallets/flask
https://github.com/tiangolo/fastapi
https://github.com/vercel/next.js
```

Or click **"Upload project files"** to upload a `.zip` of your local project.

Watch the progress bar — indexing takes:
- Small repo (< 50 files): ~30 seconds
- Medium repo (50–200 files): 1–3 minutes
- Large repo (200+ files): 3–10 minutes

### 2. Ask Questions

Once indexed, you can ask anything in natural language:

**Architecture questions:**
```
Explain the overall project architecture
What are the main modules and how do they connect?
Draw the data flow from HTTP request to database
```

**Finding code:**
```
Where is authentication handled?
Where is the database connection configured?
How is error handling implemented?
Where are environment variables loaded?
```

**Debugging:**
```
Why would the login endpoint return a 401 error?
What could cause a database connection timeout?
Why is the API rate limiter not working?
```

**Code understanding:**
```
Explain what the middleware.py file does
How does the caching layer work?
What design patterns are used in this project?
```

**Optimization:**
```
How can I optimize the database queries in user_service.py?
What's the time complexity of the search function?
```

### 3. Use Filters

In the top-right filter menu, you can narrow search:
- **Language filter:** `python`, `javascript`, `typescript`, etc.
- **Module filter:** `auth`, `api`, `models`, etc.

### 4. Read Source References

Every answer shows which files were used, with:
- File path
- Function/class name
- Line numbers
- Confidence score (0–100%)

---

## 🔧 Troubleshooting

### Backend Issues

**`ModuleNotFoundError` on startup:**
```bash
# Make sure venv is activated
venv\Scripts\activate           # Windows
source venv/bin/activate        # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

**`tree-sitter` build error on Windows:**
```bash
pip install tree-sitter --no-build-isolation
```
Also install Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/

**`faiss-cpu` installation fails:**
```bash
pip install faiss-cpu --no-cache-dir
```

**HuggingFace model download stuck:**
- First download is ~80MB, can take 2–5 minutes on slow internet
- Check internet connection
- Set `SENTENCE_TRANSFORMERS_HOME=./model_cache` to cache locally

**Groq rate limit error:**
```
Error: 429 Too Many Requests
```
Set `MULTI_QUERY_COUNT=0` in `.env` to reduce API calls.

**Flask not starting on port 5000 (macOS):**
macOS Monterey+ uses port 5000 for AirPlay. Change Flask port:
```python
# In app.py, change last line to:
app.run(debug=DEBUG, host="0.0.0.0", port=5001)
```
And update `frontend/.env.local`:
```
BACKEND_URL=http://localhost:5001
```

---

### Frontend Issues

**`next.config.js` TypeScript syntax error:**
Replace `next.config.js` content with:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [{
      source: '/api/backend/:path*',
      destination: `${process.env.BACKEND_URL || 'http://localhost:5000'}/api/:path*`,
    }]
  },
}
module.exports = nextConfig
```

**`npm install` fails:**
```bash
node --version   # must be 18+
npm --version    # must be 9+
```

**Frontend can't reach backend (CORS error):**
- Make sure Flask is running: http://127.0.0.1:5000/health
- Check `frontend/.env.local` has `BACKEND_URL=http://localhost:5000`
- Restart both servers after changing `.env`

**"Project not found" error:**
The project hasn't finished indexing or errored. Check:
```bash
curl http://localhost:5000/api/ingest/status/your_project_id
```

---

### Re-index a Project

FAISS indexes are cached. To force re-index:
```bash
# Delete the index files
rm backend/faiss_indexes/project_name.*
```

Then ingest the project again from the UI.

---

## ⚡ Performance Tips

### Fastest Free Setup (Recommended for Dev)

```env
LLM_PROVIDER=groq
LLM_MODEL=llama3-8b-8192        # 8b is 3-4x faster than 70b
GROQ_API_KEY=gsk_...

EMBEDDING_PROVIDER=huggingface
HF_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
SENTENCE_TRANSFORMERS_HOME=./model_cache

VECTOR_STORE=faiss
TOP_K=5                          # fewer chunks = faster
MULTI_QUERY_COUNT=0              # disable for speed
USE_RERANKER=false
```

### Speed Benchmarks (approximate)

| Operation | Fast config | Default config |
|-----------|------------|----------------|
| First run (model download) | 1–2 min | 1–2 min |
| Subsequent starts | 3–5s | 3–5s |
| Index small repo (30 files) | ~20s | ~45s |
| Index medium repo (100 files) | ~1 min | ~3 min |
| Query response | 2–4s | 5–10s |

### For Large Repos

If indexing a very large repo (500+ files), increase chunking:
```env
MAX_CHUNK_TOKENS=600
TOP_K=6
```

Use `mixtral-8x7b-32768` for its larger context window:
```env
LLM_MODEL=mixtral-8x7b-32768
```

---

## 🗺️ Roadmap

- [ ] **GitHub OAuth** — index private repos
- [ ] **Conversation memory** — multi-turn chat that remembers context
- [ ] **Code diff analysis** — "What changed between these two commits?"
- [ ] **Dependency graph** — visual map of how files connect
- [ ] **VS Code extension** — query DevBrain directly from your editor
- [ ] **Multiple repo support** — ask questions across multiple projects
- [ ] **Export answers** — save conversations as markdown
- [ ] **Webhook indexing** — auto re-index on git push

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

Built with:
- [LangChain](https://langchain.com) — RAG framework
- [Tree-sitter](https://tree-sitter.github.io) — Code parsing
- [Groq](https://groq.com) — Fast LLM inference
- [FAISS](https://faiss.ai) — Vector similarity search
- [sentence-transformers](https://sbert.net) — Local embeddings
- [Next.js](https://nextjs.org) — Frontend framework

---

<div align="center">
  Made with ❤️ by developers, for developers
  <br/>
  <strong>CodeAtlas — Because reading code shouldn't take weeks</strong>
</div>