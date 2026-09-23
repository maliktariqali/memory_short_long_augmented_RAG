import uuid

from db import get_connection, put_connection

class LongTermMemory:
    """
    Persistent user-level memory stored in PostgreSQL.
    Table is created by sql/schema.sql (scripts/init_db.py).
    """

    def add_memory(self, user_id: str, content: str):
        memory_id = str(uuid.uuid4())

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO long_term_memory (memory_id, user_id, content)
                    VALUES (%s, %s, %s)
                    """,
                    (memory_id, user_id, content),
                )
            connection.commit()
        finally:
            put_connection(connection)

        return memory_id

    def get_memories(self, user_id: str):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT content FROM long_term_memory
                    WHERE user_id = %s
                    ORDER BY created_at, memory_id
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()
        finally:
            put_connection(connection)

        return [row[0] for row in rows]

    def delete_user_memories(self, user_id: str):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM long_term_memory WHERE user_id = %s",
                    (user_id,),
                )
            connection.commit()
        finally:
            put_connection(connection)


long_term_memory = LongTermMemory()

