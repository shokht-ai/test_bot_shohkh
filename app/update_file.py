import os
from datetime import datetime

from aiogram.types import Message

from .handlers.base_handler import start_command
from database1.banks import update_title_and_created_time_by_bank_id, update_file_by_bank
from database1.files import update_file_name, get_bank_id_by_file_id, get_file_path_by_file_id
from database1.questions import delete_questions_by_bank_id_bulk, insert_questions_bulk



async def sort_message(msg: Message, file_path):
    file_name = msg.document.file_name
    file_id = msg.caption
    created_date = datetime.now().isoformat()
    from .uploading_file import extract_questions_from_excel, check_count_questions_in_excel
    if await check_count_questions_in_excel(msg, file_path):
        return

    bank_id = get_bank_id_by_file_id(file_id)

    if bank_id is None:
        os.remove(file_path)
        await start_command(msg, "⚠️ Bunday ID bilan fayl topilmadi.")
        return
    else:
        bank_id = bank_id[0][0]
        os.remove(get_file_path_by_file_id(bank_id)[0][0])

    update_title_and_created_time_by_bank_id(file_name, created_date, bank_id)
    update_file_name(file_id, file_path)
    delete_questions_by_bank_id_bulk(bank_id)

    questions = extract_questions_from_excel(file_path)
    insert_questions_bulk(bank_id, questions)
    update_file_by_bank(bank_id)
    await start_command(msg, "✅ Fayl bazaga muvaffaqiyatli yangilandi.")
    # file_id borligni tekshirish yo'q bo'lsa fileni downloadsdan o'chirish.
