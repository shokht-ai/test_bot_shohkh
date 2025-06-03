import asyncpg
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Database connection from .env or URL
def get_db_config():
    db_url = os.getenv("DATABASE_URL")
    print("baza manzili:", db_url)
    if db_url:
        db_params = urlparse(db_url)
        return {
            "user": db_params.username,
            "password": db_params.password,
            "database": db_params.path[1:],
            "host": db_params.hostname,
            "port": db_params.port or 5432
        }
    return {
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", ""),
        "database": os.getenv("PGDATABASE", "postgres"),
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", 5432)
    }

DB_CONFIG = get_db_config()

async def get_connection():
    return await asyncpg.connect(**DB_CONFIG)

async def execute_query(query, params=None):
    if params is None:
        params = []
    conn = await get_connection()
    try:
        await conn.execute(query, *params)
    finally:
        await conn.close()

async def fetch_all(query, params=None):
    if params is None:
        params = []
    conn = await get_connection()
    try:
        return await conn.fetch(query, *params)
    finally:
        await conn.close()
