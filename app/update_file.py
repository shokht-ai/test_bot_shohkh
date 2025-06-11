import os
# import logging
from datetime import datetime

from aiogram.types import Message

from .handlers.base_handler import start_command
from database.banks import update_title_and_created_time_by_bank_id, update_file_by_bank
from database.files import update_file_name, get_bank_id_by_file_id, get_file_path_by_file_id
from database.questions import delete_questions_by_bank_id_bulk, insert_questions_bulk

# logger = logging.getLogger(__name__)

async def sort_message(msg: Message, file_path):
    try:
        file_name = msg.document.file_name
        file_id = msg.caption
        created_date = datetime.now()
        from .uploading_file import extract_questions_from_excel, check_count_questions_in_excel
        if await check_count_questions_in_excel(msg, file_path):
            return

        bank_id = await get_bank_id_by_file_id(int(file_id))

        if bank_id is None:
            os.remove(file_path)
            await start_command(msg, "⚠️ Bunday ID bilan fayl topilmadi.")
            return
        else:
            bank_id = bank_id[0]['bank_id']
            file_removed_path = (await get_file_path_by_file_id(bank_id))[0]['file_name']
            if os.path.exists(file_removed_path):
                os.remove(file_removed_path)

        await update_title_and_created_time_by_bank_id(file_name, created_date, bank_id)
        await update_file_name(int(file_id), file_path)
        await delete_questions_by_bank_id_bulk(bank_id)

        questions = extract_questions_from_excel(file_path)
        await insert_questions_bulk(bank_id, questions)
        await update_file_by_bank(bank_id)
        await start_command(msg, "✅ Fayl bazaga muvaffaqiyatli yangilandi.")
        # file_id borligni tekshirish yo'q bo'lsa fileni downloadsdan o'chirish.
    except Exception as e:
        print(f"update_file::sort_message da xatolik\n{e}")
