#files.py
from database.shared import execute_query, fetch_all

async def create_file_table():
    await execute_query("""
        CREATE TABLE IF NOT EXISTS files (
            file_id SERIAL PRIMARY KEY,
            bank_id INTEGER,
            file_name TEXT,
            FOREIGN KEY (bank_id) REFERENCES banks(bank_id)
        );
    """)

async def insert_file_name(bank_id: int, file_name: str) -> None:
    await execute_query(
        "INSERT INTO files (bank_id, file_name) VALUES ($1, $2)",
        [bank_id, file_name]
    )

async def get_file_name_by_bank(bank_id: int):
    records = await fetch_all(
        "SELECT file_name FROM files WHERE bank_id = $1",
        [bank_id]
    )
    return [dict(record) for record in records]

async def get_file_id_by_bank_id(bank_id: int):
    records = await fetch_all(
        "SELECT file_id FROM files WHERE bank_id = $1",
        [bank_id]
    )
    return [dict(record) for record in records]

async def get_bank_id_by_file_id(file_id: int):
    records = await fetch_all(
        "SELECT bank_id FROM files WHERE file_id = $1",
        [file_id]
    )
    return [dict(record) for record in records]

async def get_file_path_by_file_id(file_id: int):
    records = await fetch_all(
        "SELECT file_name FROM files WHERE file_id = $1",
        [file_id]
    )
    return [dict(record) for record in records]

async def update_file_name(file_id: int, file_name: str):
    await execute_query(
        "UPDATE files SET file_name = $1 WHERE file_id = $2",
        [file_name, file_id]
    )
