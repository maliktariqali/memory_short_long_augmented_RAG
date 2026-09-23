from db import get_connection, put_connection

class PgVectorStore:
    """
    Generic pgvector-backed store.

    Expected table columns:
        content    TEXT
        embedding  VECTOR(EMBEDDING_DIM)
        user_id    TEXT   (only required when scoped_by_user=True)

    `table` must always be a fixed, developer-supplied constant —
    never build it from user input.
    """

    def __init__(self, embedding_service, table: str, scoped_by_user: bool = False):
        self.embedding_service = embedding_service
        self.table = table
        self.scoped_by_user = scoped_by_user

    def add(self, text: str, user_id: str = None):
        vector = self.embedding_service.embed(text)

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                if self.scoped_by_user:
                    cursor.execute(
                        f"INSERT INTO {self.table} (user_id, content, embedding) "
                        f"VALUES (%s, %s, %s)",
                        (user_id, text, vector),
                    )
                else:
                    cursor.execute(
                        f"INSERT INTO {self.table} (content, embedding) "
                        f"VALUES (%s, %s)",
                        (text, vector),
                    )
            connection.commit()
        finally:
            put_connection(connection)

    def search(self, query: str, k: int = 3, user_id: str = None):
        query_vector = self.embedding_service.embed(query)

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                if self.scoped_by_user:
                    cursor.execute(
                        f"SELECT content FROM {self.table} "
                        f"WHERE user_id = %s "
                        f"ORDER BY embedding <=> %s LIMIT %s",
                        (user_id, query_vector, k),
                    )
                else:
                    cursor.execute(
                        f"SELECT content FROM {self.table} "
                        f"ORDER BY embedding <=> %s LIMIT %s",
                        (query_vector, k),
                    )
                rows = cursor.fetchall()
        finally:
            put_connection(connection)

        return [row[0] for row in rows]

    def count(self):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {self.table}")
                return cursor.fetchone()[0]
        finally:
            put_connection(connection)

