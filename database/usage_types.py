#usage_types.py
from database.shared import execute_query, fetch_all, get_connection


async def create_usage_types_table():
    await execute_query("""
        CREATE TABLE IF NOT EXISTS usage_types (
            types_id SERIAL PRIMARY KEY,
            types_name VARCHAR(20) NOT NULL UNIQUE,
            users_amount INTEGER DEFAULT 0
        );
    """)

    # Default turlar: founder, admin, pro, ordinary
    rows = await fetch_all("SELECT types_name FROM usage_types")
    existing_types = [row["types_name"] for row in rows] if rows else []

    for type_name in ["founder", "admin", "pro", "ordinary"]:
        if type_name not in existing_types:
            await execute_query(
                """
                INSERT INTO usage_types (types_name, users_amount)
                VALUES ($1, $2)
                ON CONFLICT (types_name) DO NOTHING
                """,
                [type_name, 0]
            )

async def increase_users_amount(types_name: str):
    await execute_query(
        "UPDATE usage_types SET users_amount = users_amount + 1 WHERE types_name = $1",
        [types_name]
    )

async def get_user_type(user_id: int):
    records = await fetch_all(
        "SELECT usage_type FROM users WHERE user_id = $1",
        [user_id]
    )
    return [dict(record) for record in records]

async def get_info_types():
    records = await fetch_all(
        "SELECT types_name, users_amount FROM usage_types"
    )
    return [dict(record) for record in records]
