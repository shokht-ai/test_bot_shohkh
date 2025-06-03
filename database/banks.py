#banks.py
from database.shared import execute_query, fetch_all, get_connection
from datetime import datetime


async def dict_to_list(result) -> list:
    items = [dict(record) for record in result]
    return list(item.values() for item in items)

async def create_bank_table():
    await execute_query("""
        CREATE TABLE IF NOT EXISTS banks (
            bank_id SERIAL PRIMARY KEY,
            user_id BIGINT,
            title TEXT,
            created_at TIMESTAMP,
            capacity INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """)

async def create_bank(user_id, title):
    query = """
        INSERT INTO banks (user_id, title, created_at, capacity) 
        VALUES ($1, $2, $3, $4) 
        RETURNING bank_id
    """
    date = datetime.now()
    conn = await get_connection()
    try:
        result = await conn.fetchrow(query, user_id, title, date, 3)
        if result:
            return dict(result)
        else:
            return None
    finally:
        await conn.close()

async def get_banks_by_user(user_id: int) -> list[dict]:
    records = await fetch_all(
        "SELECT created_at, title, bank_id FROM banks WHERE user_id = $1",
        [user_id]
    )
    # asyncpg.Record obyektlarini dictlarga aylantiramiz
    return [dict(record) for record in records]

async def get_info_for_view_subs(user_id: int):
    records = await fetch_all(
        "SELECT title, capacity, bank_id FROM banks WHERE user_id = $1",
        [user_id]
    )
    return [dict(record) for record in records]

async def get_amount_by_user(user_id: int) -> list:
    records =  await fetch_all(
        "SELECT COUNT(bank_id) FROM banks WHERE user_id = $1",
        [user_id]
    )
    return [dict(record) for record in records]

async def get_amount_banks():
    records = await fetch_all("SELECT COUNT(bank_id) FROM banks")
    return [dict(record) for record in records]

async def get_capacity_by_bank(bank_id: int) -> list:
    records =  await fetch_all(
        "SELECT capacity FROM banks WHERE bank_id = $1",
        [bank_id]
    )
    return [dict(record) for record in records]

async def update_file_by_bank(bank_id: int):
    await execute_query(
        "UPDATE banks SET capacity = capacity - 1 WHERE bank_id = $1",
        [bank_id]
    )

async def update_title_and_created_time_by_bank_id(title: str, created_at: str, bank_id: int):
    await execute_query(
        "UPDATE banks SET title = $1, created_at = $2 WHERE bank_id = $3",
        [title, created_at, bank_id]
    )

async def update_capacity_by_time():
    await execute_query("UPDATE banks SET capacity = 3")
