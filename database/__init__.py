# database/init.py
import asyncio

from database.pro_keys import create_pro_key_table
from database.users import create_user_table
from database.banks import create_bank_table
from database.questions import create_question_table
from database.files import create_file_table
from database.usage_types import create_usage_types_table


async def initialize_database():
    await create_usage_types_table()
    await create_user_table()
    await create_bank_table()
    await create_question_table()
    await create_file_table()
    await create_pro_key_table()

# if __name__ == '__main__':
#     asyncio.run(initialize_database())