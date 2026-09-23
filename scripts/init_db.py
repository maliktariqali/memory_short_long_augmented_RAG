from pathlib import Path
import sys

import psycopg2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import POSTGRES_DSN

def main():
    schema_path = (
        PROJECT_ROOT
        / "sql"
        / "schema.sql"
    )

    sql = schema_path.read_text()

    connection = psycopg2.connect(POSTGRES_DSN)
    connection.autocommit = True

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
    finally:
        connection.close()

    print("Schema applied successfully.")


if __name__ == "__main__":
    main()

#python scripts/init_db.py    