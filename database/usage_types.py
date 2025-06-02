# usage_types.py
from .shared import get_cursor, execute_query, fetch_all


def create_usage_types_table():
    with get_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usage_types (
                types_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unikal, takrorlanmas, osuvchi
                types_name TEXT NOT NULL CHECK (LENGTH(types_name) <= 20),  -- tekst, maksimal 20 belgi
                users_amount INTEGER  -- foydalanuvchilar soni
            )
        """)
        # Jadvaldagi mavjud qiymatlarni tekshiramiz
        existing_types = [row[0] for row in fetch_all("SELECT types_name FROM usage_types", params=None) or []]

        for i in ["founder", "admin", "pro", "ordinary"]:
            if i not in existing_types:
                execute_query("INSERT INTO usage_types (types_name, users_amount) VALUES (?, ?)", (i, 0))

def increase_users_amount(types_name: str):
    execute_query("UPDATE usage_types SET users_amount = users_amount + 1 WHERE types_name = ?", (types_name,))


def get_user_type(user_id: int) -> list:
    return fetch_all("SELECT usage_type FROM users WHERE user_id =?", (user_id,))


def get_info_types():
    return fetch_all("SELECT types_name, users_amount FROM usage_types", params=None)
