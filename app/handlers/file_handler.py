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
    sorted_banks = sorted(banks, key=lambda b: b[1].lower())

    buttons = [
        InlineKeyboardButton(text=bank[1], callback_data=command_prefix + str(bank[2]))
        for bank in sorted_banks
    ]

    return list(chunked(buttons, 3))


@file_handler_router.message(F.text == "📥 Savollarni yuklab olish")
@file_handler_router.message(F.text == "🚀 Testni boshlash")
@file_handler_router.message(Command("test"))
@file_handler_router.message(Command('savollar'))
async def list_user_banks(message: Message):
    user_id = message.from_user.id
    banks = get_banks_by_user(user_id)

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
    banks = get_banks_by_user(user_id)

    if not banks:
        await message.answer("📭 Sizda hozircha hech qanday test yo'q.")
        return

    response = "<b>📚 Testlaringiz:</b>\n\n"
    for bank in banks:
        # Sana formatlash
        original_date = bank[0]  # bank[0] dan sana olish
        from datetime import datetime
        date_object = datetime.fromisoformat(original_date)  # ISO formatidagi sanani datetime ob'ektiga aylantirish
        formatted_date = date_object.strftime('%d-%m-%Y')  # Kun-oy-yil formatiga o'tkazish
        response += f"🔹 <b>{bank[1]}</b>\n (Yaratilgan: <code>{formatted_date}</code>),\t(Test ID: <b>{bank[2]}</b>)\n\n"
    await message.answer(response)


@file_handler_router.message()
async def no_commands(msg: Message):
    await start_command(msg, text="🤔 Kechirasiz, bu buyruqni tushunmadim. Menyudan biror amalni tanlang.")


@file_handler_router.message(Command("pro"))
async def check_founder(msg: Message):
    from database1.users import get_user_by_id
    user_type = get_user_by_id(msg.from_user.id)
    if user_type[0][0] != "founder":
        await no_commands(msg)
    else:
        await generate_unique_id(msg)

# ______________________________________________
