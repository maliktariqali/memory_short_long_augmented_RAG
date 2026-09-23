CREATE EXTENSION IF NOT EXISTS vector;

-- Component 2: Long-term memory (facts, preferences, decisions)
CREATE TABLE IF NOT EXISTS long_term_memory (
    memory_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     TEXT NOT NULL,
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_long_term_memory_user
    ON long_term_memory (user_id);

-- Component 3: Semantic memory (past interactions + embeddings, per user)
CREATE TABLE IF NOT EXISTS semantic_memory (
    memory_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     TEXT NOT NULL,
    content     TEXT NOT NULL,
    embedding   VECTOR(384) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_semantic_memory_user
    ON semantic_memory (user_id);
CREATE INDEX IF NOT EXISTS idx_semantic_memory_embedding
    ON semantic_memory USING hnsw (embedding vector_cosine_ops);

-- Component 4: RAG knowledge base (document chunks + embeddings)
CREATE TABLE IF NOT EXISTS knowledge_base (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content     TEXT NOT NULL,
    source      TEXT,
    embedding   VECTOR(384) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding
    ON knowledge_base USING hnsw (embedding vector_cosine_ops);