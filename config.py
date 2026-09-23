import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

MAX_RECENT_MESSAGES = int(
    os.getenv("MAX_RECENT_MESSAGES", "6")
)

TOP_K_DOCUMENTS = int(
    os.getenv("TOP_K_DOCUMENTS", "3")
)

TOP_K_MEMORIES = int(
    os.getenv("TOP_K_MEMORIES", "3")
)

LONG_TERM_DB_PATH = os.getenv(
    "LONG_TERM_DB_PATH",
    str(BASE_DIR / "long_term_memory.db"),
)

USE_FAKE_MODE = os.getenv(
    "USE_FAKE_MODE",
    "0",
) == "1"

## Added
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

POSTGRES_DSN = os.getenv(
    "POSTGRES_DSN",
    "postgresql://postgres:postgres@localhost:5432/memory_rag",
)

SHORT_TERM_TTL_SECONDS = int(
    os.getenv("SHORT_TERM_TTL_SECONDS", "3600")
)

EMBEDDING_DIM = int(
    os.getenv("EMBEDDING_DIM", "384")
)