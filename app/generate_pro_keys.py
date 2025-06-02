import uuid
from random import sample

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.pro_keys import create_pro_key, get_key_id_by_key, update_key_by_id, check_key_used_by_id, update_info_key
from database.shared import execute_query
from app.handlers.base_handler import start_command

pro_key_router = Router()

async def generate_unique_id(msg: Message):
    generate = uuid.uuid1()
    generate = str(generate)
    create_pro_key(generate)
    key_id = get_key_id_by_key(generate)[0][0]
    generate = " ".join([generate[:14], generate[15:]]).replace(" ", str(key_id))
    generate = str(key_id) + ":".join(sample(generate, len(generate)))
    update_key_by_id(generate, key_id)
    await start_command(msg, f"Pro obuna uchun yangi kalit:\n<pre>{generate}</pre>")


# # Vaqtinchalik funksiya
# # Ma'lumotlarni ba'zadan o'chirish uchun
# async def restart_all(msg: Message):
#     execute_query("DELETE FROM questions;")
#     execute_query("DELETE FROM banks;")
#     execute_query("DELETE FROM users;")
#     execute_query("DELETE FROM files;")
#     execute_query("DELETE FROM pro_keys;")
#     await start_command(msg, "Barchasi o'chirildi.")


# VAqtinchalik funksiya
# Foydalanuvchi tarifini orinaryga qaytarish uchun
@pro_key_router.message(Command("start_users"))
async def restart_users(msg: Message):
    user_id = msg.text
    execute_query("UPDATE users SET usage_type = ordinary WHERE user_id = ?;", (user_id,))
    await start_command(msg, f"<code>{user_id}</code>\nFoydalanuvchilarning tarifi yangilandi.")

@pro_key_router.message(F.text == "update_capacity")
async def update_capacity(msg: Message):
    if msg.from_user.id != 7895477080:
        from .handlers.file_handler import no_commands
        await no_commands(msg)
        return
    from database.banks import update_capacity_by_time
    update_capacity_by_time()

@pro_key_router.message(F.text.startswith == "/pro ")
@pro_key_router.message(Command("pro"))
async def check_key_used(msg: Message):
    get_id_list = list(msg.text.split(" "))

    if not is_valid_key_format(get_id_list):
        await start_command(msg, "Kalit mavjud emas.")
        return

    get_id = get_id_list[1]
    key_id = get_key_id(get_id)

    if not key_id or not key_id.isdigit():
        await start_command(msg, "Kalit mavjud emas.")
        return

    key_id_int = int(key_id)
    used_bool = check_key_used_by_id(key_id_int)

    if not used_bool:
        await start_command(msg, "Kalit mavjud emas.")
        return

    if used_bool[0][0] == 1:
        await start_command(msg, "Kalit allaqachon ishlatilib bo'lingan.")
        return
    elif used_bool[0][0] == 0:
        await handle_user_subscription(msg, key_id_int)

    await start_command(msg, f"Tabriklaymiz obuna tarifingiz Pro ga ko'tarildi.")


# Yordamchi funksiyalar

def is_valid_key_format(get_id_list):
    """Kalit formatini tekshiradi."""
    return len(get_id_list) == 2 and len(get_id_list[1]) == 75 and get_id_list[1].find(":") != -1


def get_key_id(get_id):
    """Kalitdan id qismini olish."""
    return get_id[:get_id.find(':') - 1]


async def handle_user_subscription(msg: Message, key_id: int):
    """Foydalanuvchini obuna yangilash uchun yordamchi funksiyani bajaradi."""
    from database.users import update_user_type, get_user_by_id

    user_id = msg.from_user.id
    info_user = get_user_by_id(user_id)

    if not info_user:
        await msg.answer("Iltimos oldin test tuzmoqchi bo'lgan faylingizni tashab qo'ying")
        return

    update_info_key(key_id)
    update_user_type(user_id, "pro")
