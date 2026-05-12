import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
LLM_PROVIDER     = os.getenv("LLM_PROVIDER", "openai")   # "openai" | "groq"
LLM_MODEL        = os.getenv("LLM_MODEL", "gpt-4o")

# ── Embeddings ────────────────────────────────────────────────────────
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")  # "openai" | "huggingface"
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
HF_EMBED_MODEL     = os.getenv("HF_EMBED_MODEL", "microsoft/codebert-base")

# ── Vector Store ──────────────────────────────────────────────────────
VECTOR_STORE    = os.getenv("VECTOR_STORE", "faiss")   # "faiss" | "pgvector"
FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "./faiss_indexes")

# pgvector
PG_HOST     = os.getenv("PG_HOST", "localhost")
PG_PORT     = os.getenv("PG_PORT", "5432")
PG_USER     = os.getenv("PG_USER", "devbrain")
PG_PASSWORD = os.getenv("PG_PASSWORD", "devbrain")
PG_DB       = os.getenv("PG_DB", "devbrain")
PG_URL      = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

# ── Retrieval ─────────────────────────────────────────────────────────
TOP_K              = int(os.getenv("TOP_K", "8"))
MULTI_QUERY_COUNT  = int(os.getenv("MULTI_QUERY_COUNT", "4"))
USE_RERANKER       = os.getenv("USE_RERANKER", "false").lower() == "true"
RERANKER_MODEL     = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# ── Chunking ──────────────────────────────────────────────────────────
MAX_CHUNK_TOKENS = int(os.getenv("MAX_CHUNK_TOKENS", "400"))

# ── App ───────────────────────────────────────────────────────────────
UPLOAD_DIR  = os.getenv("UPLOAD_DIR", "./uploads")
SECRET_KEY  = os.getenv("SECRET_KEY", "devbrain-secret-change-me")
DEBUG       = os.getenv("FLASK_DEBUG", "true").lower() == "true"

os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
