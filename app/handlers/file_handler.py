from itertools import islice

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from app.handlers.base_handler import start_command, base_handeler_router

# -------------------------
from database.banks import get_banks_by_user
from app.generate_pro_keys import generate_unique_id

# Routerlarni yuklab olamiz
from app.uploading_file import uploading_file_router
from app.view_subscription_price import subcription_router
from app.stats import stats_router
from app.generate_pro_keys import pro_key_router
from app.sending_file import sending_file_router
from app.start_poll import start_polling_router

file_handler_router = Router()

all_router = [
    file_handler_router,
    uploading_file_router,
    subcription_router,
    stats_router,
    pro_key_router,
    sending_file_router,
    start_polling_router,
    base_handeler_router,
]


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


text_triggers = ["🚀 Testni boshlash", "📥 Savollarni yuklab olish"]


@file_handler_router.message(F.text == "🚀 Testni boshlash")
@file_handler_router.message(F.text == "📥 Savollarni yuklab olish")
@file_handler_router.message(Command("test"))
@file_handler_router.message(Command("savollar"))
async def startTest_and_downloadTest(message: Message):
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
        reply_markup=inline_kb,
    )


@file_handler_router.message(F.text == "📚 Testlarim")
@file_handler_router.message(Command("testlarim"))
async def list_user_banks(message: Message):
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
        response += f"🔹 <b>{bank[1]}</b>\n (Yaratilgan: <code>{formatted_date}</code>)\n\n"
    await message.answer(response)


@file_handler_router.message(F.text.startswith == "/")
async def no_commands(msg: Message):
    await start_command(msg, text="🤔 Kechirasiz, bu buyruqni tushunmadim. Menyudan biror amalni tanlang.")


async def check_founder(msg: Message):
    from database.users import get_user_by_id
    user_type = get_user_by_id(msg.from_user.id)
    if user_type[0][0] != "founder":
        await no_commands(msg)
    else:
        await generate_unique_id(msg)
