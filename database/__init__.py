# database/init.py
from .pro_keys import create_pro_key_table
from .users import create_user_table
from .banks import create_bank_table
from .questions import create_question_table
from .files import create_file_table
from .usage_types import create_usage_types_table


def initialize_database():
    create_user_table()
    create_bank_table()
    create_question_table()
    create_file_table()
    create_usage_types_table()
    create_pro_key_table()

