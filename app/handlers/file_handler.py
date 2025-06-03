from typing import Any, Coroutine

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command

from app.handlers.base_handler import start_command
# -------------------------

from itertools import islice
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from database.banks import get_banks_by_user
from app.generate_pro_keys import generate_unique_id

file_handler_router = Router()


def chunked(data, size):
    it = iter(data)
    return iter(lambda: list(islice(it, size)), [])


def create_bank_buttons(banks, command_prefix: str):
    # created_at, title, bank_id
    sorted_banks = sorted(banks, key=lambda b: b["title"].lower())

    buttons = [
        InlineKeyboardButton(
            text=bank["title"],
            callback_data=command_prefix + str(bank["bank_id"])
        )
        for bank in sorted_banks
    ]

    return list(chunked(buttons, 3))


@file_handler_router.message(F.text == "📥 Savollarni yuklab olish")
@file_handler_router.message(F.text == "🚀 Testni boshlash")
@file_handler_router.message(Command("test"))
@file_handler_router.message(Command('savollar'))
async def list_user_banks(message: Message):
    user_id = message.from_user.id
    banks = await get_banks_by_user(user_id)
    poll_type = "test:" if message.text in ["🚀 Testni boshlash", "/test"] else "savollar:"
    inline_keyboard = create_bank_buttons(banks, poll_type)
    inline_kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    if len(inline_keyboard) == 0:
        await message.answer("📭 Sizda hozircha hech qanday test yo'q.")
        return
    await message.answer(
        "<b>📚 Testlaringiz:</b>\nIltimos, foydalanmoqchi bo'lgan testizni tanlang...\n\n",
        reply_markup=inline_kb
    )


@file_handler_router.message(F.text == "📚 Testlarim")
@file_handler_router.message(Command("testlarim"))
async def show_user_banks(message: Message):
    user_id = message.from_user.id
    # created_at, title, bank_id
    banks = await get_banks_by_user(user_id)
    # created_at, title, bank_id
    if not banks:
        await message.answer("📭 Sizda hozircha hech qanday test yo'q.")
        return

    response = "<b>📚 Testlaringiz:</b>\n\n"
    for bank in banks:
        original_date = bank["created_at"]

        # original_date odatda datetime turida bo'ladi. Tekshirib, formatlash:
        if isinstance(original_date, str):
            date_object = datetime.fromisoformat(original_date)
        else:
            date_object = original_date  # Bu allaqachon datetime.datetime bo'lishi kerak

        formatted_date = date_object.strftime('%d-%m-%Y')  # Kun-oy-yil

        response += (
            f"🔹 <b>{bank['title']}</b>\n"
            f"(Yaratilgan: <code>{formatted_date}</code>),\t"
            f"(Test ID: <b>{bank['bank_id']}</b>)\n\n"
        )

    await message.answer(response)


@file_handler_router.message()
async def no_commands(msg: Message):
    await start_command(msg, text="🤔 Kechirasiz, bu buyruqni tushunmadim. Menyudan biror amalni tanlang.")


@file_handler_router.message(Command("pro"))
async def check_founder(msg: Message):
    from database.users import get_user_by_id
    user_type = await get_user_by_id(msg.from_user.id)
    if user_type[0]['usage_type'] != "founder":
        await no_commands(msg)
    else:
        await generate_unique_id(msg)

# ______________________________________________
