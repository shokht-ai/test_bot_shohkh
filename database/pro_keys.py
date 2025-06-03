#pro_keys.py
from database.shared import execute_query, fetch_all

async def create_pro_key_table():
    await execute_query("""
        CREATE TABLE IF NOT EXISTS pro_keys (
            id SERIAL PRIMARY KEY,
            key TEXT UNIQUE,
            used INTEGER DEFAULT 0
        );
    """)

async def create_pro_key(key: str):
    await execute_query(
        "INSERT INTO pro_keys (key, used) VALUES ($1, $2)",
        [key, 0]
    )

async def check_key_used_by_id(pro_key_id: int):
    records = await fetch_all(
        "SELECT used FROM pro_keys WHERE id = $1",
        [pro_key_id]
    )
    return [dict(record) for record in records]

async def get_key_id_by_key(key: str):
    records = await fetch_all(
        "SELECT id FROM pro_keys WHERE key = $1",
        [key]
    )
    return [dict(record) for record in records]

async def update_key_by_id(key: str, pro_key_id: int):
    await execute_query(
        "UPDATE pro_keys SET key = $1 WHERE id = $2",
        [key, pro_key_id]
    )

async def update_info_key(pro_key_id: int):
    await execute_query(
        "UPDATE pro_keys SET used = $1 WHERE id = $2",
        [1, pro_key_id]
    )
