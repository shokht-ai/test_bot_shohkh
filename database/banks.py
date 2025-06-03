from .shared import get_cursor, execute_query, fetch_all
from datetime import datetime

def create_bank_table():
    execute_query("""
        CREATE TABLE IF NOT EXISTS banks (
            bank_id SERIAL PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            created_at TIMESTAMP,
            capacity INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        """)

def create_bank(user_id, title):
    query = """
        INSERT INTO banks (user_id, title, created_at, capacity) 
        VALUES (%s, %s, %s, %s) 
        RETURNING bank_id
    """
    date = datetime.now()
    with get_cursor() as cur:
        cur.execute(query, (user_id, title, date, 3))
        result = cur.fetchone()
        return result[0] if result else None

def get_banks_by_user(user_id) -> list:
    return fetch_all(
        "SELECT created_at, title, bank_id FROM banks WHERE user_id = %s",
        (user_id,)
    )

def get_info_for_view_subs(user_id: int):
    return fetch_all(
        "SELECT title, capacity, bank_id FROM banks WHERE user_id = %s",
        (user_id,)
    )

def get_amount_by_user(user_id: int) -> list:
    return fetch_all(
        "SELECT COUNT(bank_id) FROM banks WHERE user_id = %s",
        (user_id,)
    )

def get_amount_banks():
    return fetch_all("SELECT COUNT(bank_id) FROM banks")

def get_capacity_by_bank(bank_id: int) -> list:
    return fetch_all(
        "SELECT capacity FROM banks WHERE bank_id = %s",
        (bank_id,)
    )

def update_file_by_bank(bank_id: int):
    execute_query(
        "UPDATE banks SET capacity = capacity - 1 WHERE bank_id = %s",
        (bank_id,)
    )

def update_title_and_created_time_by_bank_id(title: str, created_at: str, bank_id: int):
    execute_query(
        "UPDATE banks SET title = %s, created_at = %s WHERE bank_id = %s",
        (title, created_at, bank_id,)
    )

def update_capacity_by_time():
    execute_query("UPDATE banks SET capacity = 3")