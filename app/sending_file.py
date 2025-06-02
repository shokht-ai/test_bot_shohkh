import os

from aiogram import Router
from aiogram.types import CallbackQuery, FSInputFile

from database.files import get_file_name_by_bank, get_file_id_by_bank_id

sending_file_router = Router()

@sending_file_router.callback_query(lambda c: c.data.startswith("savollar:"))
async def send_bank_file(callback: CallbackQuery):
    """
    Callback query orqali kelgan bank_id asosida unga tegishli .xlsx faylni topadi va foydalanuvchiga yuboradi.

Batafsil tafsilotlar:
    callback.data dan bank_id ni ajratib oladi (format: savollar:<bank_id>)

    get_file_name_by_bank(bank_id) funksiyasi yordamida fayl manzilini topadi

    Fayl mavjudligini os.path.exists orqali tekshiradi

    Agar fayl mavjud bo‘lsa, FSInputFile orqali hujjat sifatida yuboradi

    Aks holda, foydalanuvchiga “fayl topilmadi” degan xabar yuboriladi
    :param callback:
    :return:
    """
    await callback.answer()
    parts = callback.data.split(":")
    if len(parts) != 2 or not parts[1].isdigit():
        await callback.answer("❌ Noto‘g‘ri format.", show_alert=True)
        return

    bank_id = int(parts[1])
    file_id = get_file_id_by_bank_id(bank_id)[0][0]
    file_path = get_file_name_by_bank(bank_id)[0][0]
    if not os.path.exists(file_path):
        await callback.message.answer("❌ Fayl topilmadi.")
        return

    await callback.message.answer_document(
        document=FSInputFile(file_path),
        caption=f"📝 <b>Test Fayli</b> 📂\n\n"
                f"📊 <b>Bazadagi fayl <code>ID</code> si:</b> \"{file_id}\"\n"
                "Savollar va javoblarni topish uchun bu faylni yuklab oling!"
    )