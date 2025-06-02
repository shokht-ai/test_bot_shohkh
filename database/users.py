# users.py
from .shared import get_cursor, execute_query, fetch_all
from .usage_types import increase_users_amount


def create_user_table():
    with get_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                username TEXT,
                usage_type TEXT  -- 'ordinary' yoki 'premium'
            )
        """)


def create_user_if_not_exists(user_id, chat_id, username, usage_type='ordinary'):
    # Foydalanuvchi mavjudligini tekshirish
    result = fetch_all("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not result:
        # Foydalanuvchi mavjud bo'lmasa, qo'shamiz
        if user_id == 7895477080:
            usage_type = "founder"
        execute_query(
            "INSERT INTO users (user_id, chat_id, username, usage_type) VALUES (?, ?, ?, ?)",
            (user_id, chat_id, username, usage_type)
        )
        increase_users_amount(usage_type)


def get_user_by_id(user_id):
    return fetch_all("SELECT usage_type FROM users WHERE user_id = ?", (user_id,))


def get_amount_users():
    return fetch_all("SELECT COUNT(user_id) FROM users", params=None)


def update_user_type(user_id, new_type):
    execute_query("UPDATE users SET usage_type = ? WHERE user_id = ?", (new_type, user_id))
