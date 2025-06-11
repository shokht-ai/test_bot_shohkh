import os
import logging
from aiogram import Router
from aiogram.types import CallbackQuery, FSInputFile
from database.files import get_file_name_by_bank, get_file_id_by_bank_id
from dotenv import load_dotenv

load_dotenv()

sending_file_router = Router()

# Logger sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@sending_file_router.callback_query(lambda c: c.data.startswith("savollar:"))
async def send_bank_file(callback: CallbackQuery):
    """
    Callback query orqali kelgan bank_id asosida unga tegishli .xlsx faylni topadi va foydalanuvchiga yuboradi.
    """
    try:
        await callback.answer()
        parts = callback.data.split(":")
        if len(parts) != 2 or not parts[1].isdigit():
            await callback.answer("❌ Noto‘g‘ri format.", show_alert=True)
            return

        bank_id = int(parts[1])
        file_id_data = await get_file_id_by_bank_id(bank_id)
        file_name_data = await get_file_name_by_bank(bank_id)

        if not file_id_data or not file_name_data:
            await callback.message.answer("❌ Fayl haqidagi ma'lumotlar topilmadi.")
            return

        file_id = file_id_data[0]["file_id"]
        file_path = file_name_data[0]["file_name"]

        if not os.path.exists(file_path):
            await callback.message.answer("ℹ️ Yangilanish sababli ayrim fayllar o‘chirildi. Tiklash ustida ishlayapmiz.")
            return

        await callback.message.answer_document(
            document=FSInputFile(file_path),
            caption=(
                f"📝 <b>Test Fayli</b> 📂\n\n"
                f"📊 <b>Bazadagi fayl <code>ID</code> si:</b> \"{file_id}\"\n"
                "Savollar va javoblarni topish uchun bu faylni yuklab oling!"
            )
        )
    except Exception as e:
        logger.exception(f"sending_file::Xatolik yuz berdi\n{e}")
        await callback.message.answer("⚠️ Ichki xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.")
