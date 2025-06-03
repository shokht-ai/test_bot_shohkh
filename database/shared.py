import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# Configuration with URL or separate parameters
POSTGRES_URL = os.getenv("DATABASE_URL")
if POSTGRES_URL:
    db_params = urlparse(POSTGRES_URL)
    DB_CONFIG = {
        "host": db_params.hostname,
        "port": db_params.port,
        "dbname": db_params.path[1:],
        "user": db_params.username,
        "password": db_params.password
    }
else:
    DB_CONFIG = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "dbname": os.getenv("POSTGRES_DB", "postgres"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "")
    }

# Connection pool setup
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        **DB_CONFIG
    )
except Exception as e:
    print(f"Connection pool error: {e}")
    connection_pool = None

def get_connection():
    if POSTGRES_URL:
        return psycopg2.connect(POSTGRES_URL)
    if connection_pool:
        return connection_pool.getconn()
    return psycopg2.connect(**DB_CONFIG)

def release_connection(conn):
    if connection_pool:
        connection_pool.putconn(conn)
    else:
        conn.close()

@contextmanager
def get_cursor():
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        release_connection(conn)

def execute_query(query, params=None):
    if params is None:
        params = []
    with get_cursor() as cur:
        cur.execute(query, params)

def fetch_all(query, params=None):
    if params is None:
        params = []
    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()

def fetch_one(query, params=None):
    if params is None:
        params = []
    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()