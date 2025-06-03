#users.py
from database.shared import execute_query, fetch_all, get_connection
from database.usage_types import increase_users_amount
from datetime import datetime

async def dict_to_list(result) -> list:
    items = [dict(record) for record in result]
    return list(item.values() for item in items)


async def create_user_table():
    await execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            chat_id BIGINT,
            username VARCHAR(100),
            usage_type VARCHAR(20) DEFAULT 'ordinary',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usage_type) REFERENCES usage_types(types_name)
        );
    """)
    await execute_query("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
    await execute_query("CREATE INDEX IF NOT EXISTS idx_users_usage_type ON users(usage_type)")


async def create_user_if_not_exists(user_id, chat_id, username, usage_type='ordinary'):
    query_exists = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = $1)"
    result = await fetch_all(query_exists, [user_id])

    if not result[0]["exists"]:
        if user_id == 7895477080:
            usage_type = "founder"

        await execute_query(
            """INSERT INTO users (user_id, chat_id, username, usage_type) 
               VALUES ($1, $2, $3, $4)""",
            [user_id, chat_id, username, usage_type]
        )

        await increase_users_amount(usage_type)


async def get_user_by_id(user_id):
    records = await fetch_all(
        "SELECT usage_type FROM users WHERE user_id = $1",
        [user_id]
    )
    return [dict(record) for record in records]


async def get_amount_users():
    records = await fetch_all("SELECT COUNT(user_id) FROM users")
    return [dict(record) for record in records]

async def update_user_type(user_id, new_type):
    await execute_query(
        "UPDATE users SET usage_type = $1 WHERE user_id = $2",
        [new_type, user_id]
    )
