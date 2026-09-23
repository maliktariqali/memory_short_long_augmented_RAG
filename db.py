import psycopg2
import psycopg2.pool
from pgvector.psycopg2 import register_vector

from config import POSTGRES_DSN

_pg_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=POSTGRES_DSN,
)


def get_connection():
    connection = _pg_pool.getconn()
    register_vector(connection)
    return connection


def put_connection(connection):
    _pg_pool.putconn(connection)