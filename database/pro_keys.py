from database.shared import get_cursor, execute_query, fetch_all


# create table ni __init__ ga qo'shish kerak
# foydalanuvchilarga pro berish uchun birmatalik kalit yasab keyin foydalanganda uni o'chirish
def create_pro_key_table():
    with get_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pro_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                used INTEGER
            )
        """)


def create_pro_key(key: str):
    execute_query("INSERT INTO pro_keys (key, used) VALUES (?, ?)", (key, 0,))


def check_key_used_by_id(pro_key_id: int) -> list:
    return fetch_all("SELECT used FROM pro_keys WHERE id = ?", (pro_key_id,))


def get_key_id_by_key(key: str) -> list:
    return fetch_all("SELECT id FROM pro_keys WHERE key = ?", (key,))


def update_key_by_id(key: str, pro_key_id: int):
    execute_query("UPDATE pro_keys SET key = ? WHERE id = ?", (key, pro_key_id,))


def update_info_key(pro_key_id: int):
    execute_query("UPDATE pro_keys SET used = ? WHERE id = ?", (1, pro_key_id))
