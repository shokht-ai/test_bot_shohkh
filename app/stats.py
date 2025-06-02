from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .handlers.base_handler import start_command
from database.banks import get_amount_banks
from database.usage_types import get_info_types
from database.users import get_amount_users, get_user_by_id

stats_router = Router()

@stats_router.message(Command("info_bot"))
async def info_bot_stats(msg: Message):
    client_type = get_user_by_id(msg.from_user.id)[0][0]
    if client_type != "founder":
        from .handlers.file_handler import no_commands
        await no_commands(msg)
        return
    amount_banks = get_amount_banks()[0][0]
    amount_users = get_amount_users()[0][0]
    info_types = get_info_types()

    respond_text = (
        f"📊 <b>Bot statistikasi:</b>\n\n"
        f"👥 Umumiy foydalanuvchilar: <b>{amount_users}</b>\n"
        f"🗂 Saqlangan test bazalari: <b>{amount_banks}</b>\n\n"
        f"📌 <b>Test turlari bo‘yicha taqsimot:</b>\n"
    )
    for type_name, type_amount in info_types:
        respond_text += f"• <b>{type_name}</b> : {type_amount} ta\n"

    await start_command(msg, respond_text)
