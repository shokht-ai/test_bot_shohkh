from database1.shared import get_cursor, execute_query, fetch_all

def create_pro_key_table():
    execute_query("""
        CREATE TABLE IF NOT EXISTS pro_keys (
            id SERIAL PRIMARY KEY,
            key TEXT UNIQUE,
            used INTEGER DEFAULT 0
        )
    """)

def create_pro_key(key: str):
    execute_query(
        "INSERT INTO pro_keys (key, used) VALUES (%s, %s)",
        (key, 0)
    )

def check_key_used_by_id(pro_key_id: int) -> list:
    return fetch_all(
        "SELECT used FROM pro_keys WHERE id = %s",
        (pro_key_id,)
    )

def get_key_id_by_key(key: str) -> list:
    return fetch_all(
        "SELECT id FROM pro_keys WHERE key = %s",
        (key,)
    )

def update_key_by_id(key: str, pro_key_id: int):
    execute_query(
        "UPDATE pro_keys SET key = %s WHERE id = %s",
        (key, pro_key_id)
    )

def update_info_key(pro_key_id: int):
    execute_query(
        "UPDATE pro_keys SET used = %s WHERE id = %s",
        (1, pro_key_id)
    )