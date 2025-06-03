# database/init.py
from database.pro_keys import create_pro_key_table
from database.users import create_user_table
from database.banks import create_bank_table
from database.questions import create_question_table
from database.files import create_file_table
from database.usage_types import create_usage_types_table


def initialize_database():
    create_user_table()
    create_bank_table()
    create_question_table()
    create_file_table()
    create_usage_types_table()
    create_pro_key_table()

