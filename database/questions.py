# questions.py
from .shared import get_cursor, execute_query, fetch_all


def create_question_table():
    with get_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_id INTEGER,
                question TEXT,
                correct TEXT,
                wrong1 TEXT,
                wrong2 TEXT,
                wrong3 TEXT,
                FOREIGN KEY (bank_id) REFERENCES banks(bank_id)
            )
        """)


def insert_questions_bulk(bank_id: int, question_list: list):
    for q in question_list:
        execute_query("""
            INSERT INTO questions (bank_id, question, correct, wrong1, wrong2, wrong3)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            bank_id,
            q["question"],
            q["correct"],
            q["wrong1"],
            q["wrong2"],
            q["wrong3"],
        ))


def delete_questions_by_bank_id_bulk(bank_id: int) -> None:
    """
    Funksiya ma'lumotlar bazasidan test id bilan yozilgan barcha qatorlarni o'chiradi.
    :param bank_id:
    :return: None
    """
    execute_query("""
        DELETE FROM questions
        WHERE bank_id = ?
    """, (bank_id,))


def get_questions_by_bank(bank_id):
    return fetch_all("SELECT question, correct, wrong1, wrong2, wrong3 FROM questions WHERE bank_id = ?", (bank_id,))


def delete_questions_by_bank(bank_id):
    execute_query("DELETE FROM questions WHERE bank_id = ?", (bank_id,))
