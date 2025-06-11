import uuid
import os
from random import sample
import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from app.handlers.base_handler import start_command
from database.pro_keys import create_pro_key, get_key_id_by_key, update_key_by_id, check_key_used_by_id, update_info_key
from database.shared import execute_query

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pro_key_router = Router()

USER_ID = os.getenv("USERID", "123456789")

async def generate_unique_id(msg: Message):
    try:
        generate = uuid.uuid1()
        generate = str(generate)
        await create_pro_key(generate)
        key_id = await get_key_id_by_key(generate)
        key_id = key_id[0]['id']
        generate = " ".join([generate[:14], generate[15:]]).replace(" ", str(key_id))
        generate = str(key_id) + ":".join(sample(generate, len(generate)))
        await update_key_by_id(generate, key_id)
        await start_command(msg, f"Pro obuna uchun yangi kalit:\n<pre>/pro {generate}</pre>")
    except Exception as e:
        logger.info(f"generate_pro_keys::generate_unique_id xatolik yuz berdi\n{e}")

@pro_key_router.message(Command("start_users:"))
async def restart_users(msg: Message):
    try:
        if msg.from_user.id == int(USER_ID):
            user_id = int(msg.text.split(":")[1])
            from database.users import update_user_type
            await update_user_type(user_id, "ordinary")
            await start_command(msg, f"<code>{user_id}</code>\nFoydalanuvchilarning tarifi yangilandi.")
        else:
            from app.handlers.file_handler import no_commands
            await no_commands(msg)
    except Exception as e:
        logger.info(f"generate_pro_keys::restart_users xatolik yuz berdi\n{e}")

@pro_key_router.message(Command("update_capacity"))
async def update_capacity(msg: Message):
    try:
        if msg.from_user.id != int(USER_ID):
            from app.handlers.file_handler import no_commands
            await no_commands(msg)
            return
        from database.banks import update_capacity_by_time
        await update_capacity_by_time()
    except Exception as e:
        logger.info(f"generate_pro_keys::update_capacity xatolik yuz berdi\n{e}")

@pro_key_router.message(F.text.startswith == "/pro ")
async def check_key_used(msg: Message):
    try:
        get_id_list = list(msg.text.split(" "))

        if not is_valid_key_format(get_id_list):
            await start_command(msg, "Kalit mavjud emas")
            return

        key_id = get_key_id(get_id_list[1])

        if not key_id or not key_id.isdigit():
            await start_command(msg, "Kalit mavjud emas‰‰️")
            return

        key_id_int = int(key_id)
        used_bool = await check_key_used_by_id(key_id_int)

        if not used_bool:
            await start_command(msg, "Kalit mavjud emas.")
            return

        if used_bool[0]['used'] == 1:
            await start_command(msg, "Kalit allaqachon ishlatilib bo'lingan.")
            return
        elif used_bool[0]['used'] == 0:
            await handle_user_subscription(msg, key_id_int)

        await start_command(msg, f"Tabriklaymiz obuna tarifingiz Pro ga ko'tarildi.")
    except Exception as e:
        logger.info(f"generate_pro_keys::check_key_used xatolik yuz berdi\n{e}")

def is_valid_key_format(get_id_list):
    return len(get_id_list) == 2 and len(get_id_list[1]) == 75 and get_id_list[1].find(":") != -1

def get_key_id(get_id):
    return get_id[:get_id.find(':') - 1]

async def handle_user_subscription(msg: Message, key_id: int):
    try:
        from database.users import update_user_type, get_user_by_id
        user_id = msg.from_user.id
        info_user = await get_user_by_id(user_id)

        if not info_user:
            await msg.answer("Iltimos oldin test tuzmoqchi bo'lgan faylingizni tashab qo'ying")
            return

        await update_info_key(key_id)
        await update_user_type(user_id, "pro")
    except Exception as e:
        logger.info(f"generate_pro_keys::handle_user_subscription xatolik yuz berdi\n{e}")
