# Memory-Augmented RAG — Modular Demo

This project demonstrates a chat assistant that draws on four different information sources:

1. **Short-term memory** — recent messages for one session, backed by **Redis**.
2. **Long-term memory** — persistent user facts, stored in **PostgreSQL**.
3. **Semantic memory** — relevant previous interactions, retrieved by vector similarity from **PostgreSQL + pgvector**.
4. **RAG knowledge base** — business/domain documents, retrieved by vector similarity from **PostgreSQL + pgvector**.

Each of the four sources is a small, swappable module so you can see how a production memory-augmented RAG system is typically decomposed.

## Architecture

```text
Current Query
    |
    +--> Short-Term Memory (Redis)
    +--> Long-Term Memory (PostgreSQL)
    +--> Semantic Memory (PostgreSQL + pgvector)
    +--> RAG Knowledge Base (PostgreSQL + pgvector)
              |
              v
         Context Fusion
              |
              v
             LLM
              |
              v
            Answer
              |
              +--> Update short-term memory (Redis)
              +--> Update semantic memory (PostgreSQL + pgvector)
              +--> Save explicit long-term memory when user writes:
                   Remember: ...
```

## Prerequisites

- Python 3.10+
- Docker and Docker Compose (to run PostgreSQL/pgvector and Redis locally)
- An OpenAI API key — only required for real mode (chat generation and embeddings). Not needed to run the offline self-test.

## 1. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Start PostgreSQL (pgvector) and Redis

The app needs a running Postgres instance with the `pgvector` extension and a running Redis instance. `docker-compose.yml` provides both:

```bash
docker compose up -d
```

This starts:

- `postgres` — `pgvector/pgvector:pg16` on `localhost:5432` (db `memory_rag`, user/password `postgres`/`postgres`)
- `redis` — `redis:7-alpine` on `localhost:6379`

## 4. Apply the database schema

```bash
python scripts/init_db.py
```

This runs `sql/schema.sql`, which enables the `vector` extension and creates the `long_term_memory`, `semantic_memory`, and `knowledge_base` tables (the latter two with `hnsw` vector indexes).

## 5. Configure environment variables

Copy `.env.example` to `.env` and fill in your values, or export them directly. At minimum, set your OpenAI key:

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY="your-key"
```

### macOS/Linux

```bash
export OPENAI_API_KEY="your-key"
```

See [Configuration](#configuration) below for the full list of variables, including `POSTGRES_DSN` and `REDIS_URL` if you're not using the default Docker Compose setup.

## 6. Run the app

```bash
python main.py
```

Try:

```text
Remember: I prefer concise answers.
How long is the probation period?
How many paid leaves do employees receive?
```

## 7. Run the offline self-test

The self-test does **not** call OpenAI and does **not** download the `sentence-transformers` model — it runs the LLM and embedding services in a deterministic fake mode instead. It still connects to a real, running **PostgreSQL** and **Redis** (the same ones started in step 3) to verify persistence, so make sure `docker compose up -d` has been run first.

```bash
python self_test.py
```

Expected:

```text
ALL OFFLINE TESTS PASSED
```

## Configuration

All variables are read in `config.py` (via `python-dotenv`, from a `.env` file if present).

| Variable                | Default                                                | Purpose                                                 |
| ------------------------ | ------------------------------------------------------ | -------------------------------------------------------- |
| `OPENAI_API_KEY`        | —                                                      | Required in real mode; used by the OpenAI client         |
| `OPENAI_MODEL`          | `gpt-4.1-mini`                                         | Chat completion model                                    |
| `EMBEDDING_MODEL`       | `sentence-transformers/all-MiniLM-L6-v2`               | Embedding model for semantic memory and RAG              |
| `EMBEDDING_DIM`         | `384`                                                  | Must match the embedding model and `sql/schema.sql`      |
| `MAX_RECENT_MESSAGES`   | `6`                                                     | Max messages kept per session in short-term memory       |
| `SHORT_TERM_TTL_SECONDS`| `3600`                                                 | Redis TTL for an idle session                             |
| `TOP_K_DOCUMENTS`       | `3`                                                     | Documents retrieved from the RAG knowledge base per query|
| `TOP_K_MEMORIES`        | `3`                                                     | Past interactions retrieved from semantic memory per query|
| `REDIS_URL`             | `redis://localhost:6379/0`                             | Redis connection string (short-term memory)               |
| `POSTGRES_DSN`          | `postgresql://postgres:postgres@localhost:5432/memory_rag` | Postgres connection string (long-term/semantic memory, RAG)|
| `USE_FAKE_MODE`         | `0`                                                     | `1` enables deterministic fake LLM/embeddings (used by `self_test.py`) |

## Notes

- Semantic memory and the RAG knowledge base both use pgvector's cosine distance operator (`<=>`) for similarity search inside PostgreSQL — there's no separate in-process vector index.
- Short-term memory is a capped Redis list per `user_id:session_id`, trimmed to `MAX_RECENT_MESSAGES` and expiring after `SHORT_TERM_TTL_SECONDS` of inactivity.
- Long-term memory, semantic memory, and the knowledge base are all persistent (PostgreSQL) and survive restarts; only short-term memory expires.
- In fake mode (`USE_FAKE_MODE=1`), embeddings are generated with a deterministic local hash function instead of `sentence-transformers`, and the LLM response is produced by simple pattern matching — this keeps `self_test.py` fast and free of external API calls while still exercising the real Postgres/Redis storage layer.
- `vector_store.py`'s `table` parameter must always be a fixed, developer-supplied constant, never built from user input.

| Component                        | What is stored                              | DB used here (and other common options)                                           |
| --------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Short-term memory**             | Recent chat/session messages                | **Redis** (alternatives: PostgreSQL, DynamoDB, MongoDB)                             |
| **Long-term memory**              | User facts, preferences, profile, decisions | **PostgreSQL** (alternatives: MongoDB, DynamoDB, MySQL, SQLite)                     |
| **Semantic memory**               | Previous interactions + embeddings          | **PostgreSQL + pgvector** (alternatives: Qdrant, Pinecone, Weaviate, Milvus, Chroma, OpenSearch) |
| **RAG knowledge base**            | Document chunks + embeddings                | **PostgreSQL + pgvector** (alternatives: Qdrant, Pinecone, Weaviate, Milvus, OpenSearch, Elasticsearch, FAISS) |
| **Conversation history / audit**  | Full chat logs                              | Not implemented here — PostgreSQL, MongoDB, DynamoDB, S3 are common choices         |
| **Metadata**                      | document_id, user_id, source, timestamps    | PostgreSQL, MongoDB, DynamoDB                                                       |

This is a scalable, production-oriented architecture: separating short-term memory, long-term memory, semantic memory, and the RAG knowledge layer lets each component scale independently.
