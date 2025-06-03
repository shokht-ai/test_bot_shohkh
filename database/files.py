from .shared import get_cursor, execute_query, fetch_all

def create_file_table():
    execute_query("""
        CREATE TABLE IF NOT EXISTS files (
            file_id SERIAL PRIMARY KEY,
            bank_id INTEGER,
            file_name TEXT,
            FOREIGN KEY (bank_id) REFERENCES banks(bank_id)
        )
    """)

def insert_file_name(bank_id: int, file_name: str) -> None:
    """
    Funksiya faylning test id si bilan fayl nomini ma'lumotlar bazasiga qo'shadi.
    :param bank_id: Bank IDsi
    :param file_name: Fayl nomi
    :return: None
    """
    execute_query("""
        INSERT INTO files (bank_id, file_name)
        VALUES (%s, %s)
    """, (bank_id, file_name))

def get_file_name_by_bank(bank_id):
    return fetch_all(
        "SELECT file_name FROM files WHERE bank_id = %s",
        (bank_id,)
    )

def get_file_id_by_bank_id(bank_id):
    return fetch_all(
        "SELECT file_id FROM files WHERE bank_id = %s",
        (bank_id,)
    )

def get_bank_id_by_file_id(file_id):
    return fetch_all(
        "SELECT bank_id FROM files WHERE file_id = %s",
        (file_id,)
    )

def get_file_path_by_file_id(file_id):
    return fetch_all(
        "SELECT file_name FROM files WHERE file_id = %s",
        (file_id,)
    )

def update_file_name(file_id, file_name):
    execute_query(
        "UPDATE files SET file_name = %s WHERE file_id = %s",
        (file_name, file_id)
    )