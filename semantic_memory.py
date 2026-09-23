from embeddings import embedding_service
from vector_store import PgVectorStore

class SemanticMemory:
    """
    User-level semantic memory: previous interactions + embeddings,
    stored in the `semantic_memory` pgvector table.
    """

    def __init__(self):
        self.store = PgVectorStore(
            embedding_service,
            table="semantic_memory",
            scoped_by_user=True,
        )

    def add_memory(self, user_id: str, text: str):
        self.store.add(text, user_id=user_id)

    def search(self, user_id: str, query: str, k: int = 3):
        return self.store.search(query, k=k, user_id=user_id)


semantic_memory = SemanticMemory()

