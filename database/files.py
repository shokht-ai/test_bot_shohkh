from .shared import get_cursor, execute_query, fetch_all


def create_file_table():
    with get_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_id INTEGER,
                file_name TEXT --Fayl nomini saqlash uchun
            )
        """)


def insert_file_name(bank_id: int, file_name: str) -> None:
    """
    Funksiya faylning test id si bilan fayl nomini ma'lumotlar bazasiga qo'shadi.
    :param bank_id:
    :param file_name:
    :return: None
    """
    execute_query("""
        INSERT INTO files (bank_id, file_name)
        VALUES (?, ?)
    """, (
        bank_id,
        file_name
    ))


def get_file_name_by_bank(bank_id):
    return fetch_all("SELECT file_name FROM files WHERE bank_id = ?", (bank_id,))


def get_file_id_by_bank_id(bank_id):
    return fetch_all("SELECT file_id FROM files WHERE bank_id = ?", (bank_id,))


def get_bank_id_by_file_id(file_id):
    return fetch_all("SELECT bank_id FROM files WHERE file_id = ?", (file_id,))


def update_file_name(file_id, file_name):
    execute_query("UPDATE files SET file_name = ? WHERE file_id = ?", (file_name, file_id,))
