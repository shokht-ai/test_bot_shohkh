from .shared import get_cursor, execute_query, fetch_all


def create_usage_types_table():
    execute_query("""
        CREATE TABLE IF NOT EXISTS usage_types (
            types_id SERIAL PRIMARY KEY,
            types_name VARCHAR(20) NOT NULL UNIQUE,
            users_amount INTEGER DEFAULT 0
        )
    """)

    # Check existing types and insert default ones if missing
    existing_types = [row[0] for row in fetch_all("SELECT types_name FROM usage_types") or []]

    for i in ["founder", "admin", "pro", "ordinary"]:
        if i not in existing_types:
            execute_query(
                "INSERT INTO usage_types (types_name, users_amount) VALUES (%s, %s) ON CONFLICT (types_name) DO NOTHING",
                (i, 0)
            )


def increase_users_amount(types_name: str):
    execute_query(
        "UPDATE usage_types SET users_amount = users_amount + 1 WHERE types_name = %s",
        (types_name,)
    )


def get_user_type(user_id: int) -> list:
    return fetch_all(
        "SELECT usage_type FROM users WHERE user_id = %s",
        (user_id,)
    )


def get_info_types():
    return fetch_all(
        "SELECT types_name, users_amount FROM usage_types"
    )