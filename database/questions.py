#questions.py
from database.shared import execute_query, fetch_all, get_connection

async def create_question_table():
    await execute_query("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            bank_id INTEGER,
            question TEXT,
            correct TEXT,
            wrong1 TEXT,
            wrong2 TEXT,
            wrong3 TEXT,
            FOREIGN KEY (bank_id) REFERENCES banks(bank_id) ON DELETE CASCADE
        );
    """)

async def insert_questions_bulk(bank_id: int, question_list: list):
    """
    Asinxron holda savollarni bulk tarzda qo'shish.
    """
    query = """
        INSERT INTO questions (bank_id, question, correct, wrong1, wrong2, wrong3)
        VALUES ($1, $2, $3, $4, $5, $6)
    """
    conn = await get_connection()
    try:
        async with conn.transaction():
            for q in question_list:
                await conn.execute(query, bank_id, q["question"], q["correct"], q["wrong1"], q["wrong2"], q["wrong3"])
    finally:
        await conn.close()

async def delete_questions_by_bank_id_bulk(bank_id: int):
    await execute_query(
        "DELETE FROM questions WHERE bank_id = $1",
        [bank_id]
    )

async def get_questions_by_bank(bank_id: int):
    records = await fetch_all(
        """
        SELECT question, correct, wrong1, wrong2, wrong3 
        FROM questions 
        WHERE bank_id = $1
        """,
        [bank_id]
    )
    return [dict(record) for record in records]

async def delete_questions_by_bank(bank_id: int):
    await execute_query(
        "DELETE FROM questions WHERE bank_id = $1",
        [bank_id]
    )
