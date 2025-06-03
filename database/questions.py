from .shared import get_cursor, execute_query, fetch_all


def create_question_table():
    execute_query("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            bank_id INTEGER,
            question TEXT,
            correct TEXT,
            wrong1 TEXT,
            wrong2 TEXT,
            wrong3 TEXT,
            FOREIGN KEY (bank_id) REFERENCES banks(bank_id) ON DELETE CASCADE
        )
    """)


def insert_questions_bulk(bank_id: int, question_list: list):
    # Using executemany for bulk insert for better performance
    query = """
        INSERT INTO questions (bank_id, question, correct, wrong1, wrong2, wrong3)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    data = [(bank_id, q["question"], q["correct"], q["wrong1"], q["wrong2"], q["wrong3"])
            for q in question_list]

    with get_cursor() as cur:
        cur.executemany(query, data)


def delete_questions_by_bank_id_bulk(bank_id: int) -> None:
    """
    Funksiya ma'lumotlar bazasidan test id bilan yozilgan barcha qatorlarni o'chiradi.
    :param bank_id: Bank IDsi
    :return: None
    """
    execute_query("""
        DELETE FROM questions
        WHERE bank_id = %s
    """, (bank_id,))


def get_questions_by_bank(bank_id):
    return fetch_all(
        """SELECT question, correct, wrong1, wrong2, wrong3 
           FROM questions 
           WHERE bank_id = %s""",
        (bank_id,)
    )


def delete_questions_by_bank(bank_id):
    execute_query(
        "DELETE FROM questions WHERE bank_id = %s",
        (bank_id,)
    )