from embeddings import embedding_service
from vector_store import PgVectorStore

class KnowledgeBase:
    """
    RAG knowledge base for business/domain documents,
    stored in the `knowledge_base` pgvector table.
    """

    def __init__(self):
        self.store = PgVectorStore(
            embedding_service,
            table="knowledge_base",
            scoped_by_user=False,
        )

    def add_document(self, text: str):
        self.store.add(text.strip())

    def search(self, query: str, k: int = 3):
        return self.store.search(query, k=k)

    def count(self):
        return self.store.count()

knowledge_base = KnowledgeBase()

