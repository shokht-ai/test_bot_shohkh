from .shared import get_cursor, execute_query, fetch_all
from .usage_types import increase_users_amount


def create_user_table():
    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            chat_id BIGINT,
            username VARCHAR(100),
            usage_type VARCHAR(20) DEFAULT 'ordinary',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usage_type) REFERENCES usage_types(types_name)
        )
    """)
    # Create index for better performance on user lookups
    execute_query("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
    execute_query("CREATE INDEX IF NOT EXISTS idx_users_usage_type ON users(usage_type)")


def create_user_if_not_exists(user_id, chat_id, username, usage_type='ordinary'):
    # Check if user exists using more efficient EXISTS syntax
    user_exists = fetch_all(
        "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)",
        (user_id,)
    )

    if not user_exists[0][0]:  # If user doesn't exist
        # Special case for founder user
        if user_id == 7895477080:
            usage_type = "founder"

        execute_query(
            """INSERT INTO users (user_id, chat_id, username, usage_type) 
               VALUES (%s, %s, %s, %s)""",
            (user_id, chat_id, username, usage_type)
        )
        increase_users_amount(usage_type)


def get_user_by_id(user_id):
    return fetch_all(
        "SELECT usage_type FROM users WHERE user_id = %s",
        (user_id,)
    )


def get_amount_users():
    return fetch_all("SELECT COUNT(user_id) FROM users")


def update_user_type(user_id, new_type):
    execute_query(
        """UPDATE users SET usage_type = %s 
           WHERE user_id = %s""",
        (new_type, user_id)
    )