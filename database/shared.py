# shared.py
import sqlite3
from contextlib import contextmanager

DB_PATH = "./data.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


@contextmanager
def get_cursor():
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    finally:
        conn.close()


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
