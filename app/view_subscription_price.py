from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.users import get_user_by_id
from database.banks import get_info_for_view_subs, get_amount_by_user
from database.users import create_user_if_not_exists
from database.files import get_file_id_by_bank_id
from app.handlers.base_handler import start_command

subscripition_router =Router()

async def view_test_base_info(msg: Message, user_id, info):
    amount_base = (await get_amount_by_user(user_id))[0]["count"]
    usage_type = (await get_user_by_id(user_id))[0]["usage_type"]
    respond_text = f"🌟 Sizning test bazangizda hozirda <b>{amount_base}</b> ta test mavjud! 🎉\n\n"

    if amount_base == 0:
        respond_text += "Afsuski, hozirda test bazangizda hech qanday test mavjud emas. 😕 Yangi testlar yaratishni boshlash uchun vaqt toping! ⏳\n"
    else:
        respond_text += "Mana, sizda mavjud bo'lgan testlar: 📚\n\n"
        for items in info:
            title, bank_id, capacity = items["title"], items["bank_id"], items["capacity"]
            if usage_type == "founder":
                capacity = -1
            file_id = (await get_file_id_by_bank_id(bank_id))[0]["file_id"]
            respond_text += (
                f"🔹 <b>{title}</b> (Fayl ID: <code>{file_id}</code>)\n"
                f"    🌱 Faylni <b>{capacity}</b> marta yangilay olasiz. 🔄\n\n"
            )

    # Foydalanuvchiga ko'proq yordam va motivatsiya berish
    respond_text += (
        "Agar yangi testlar yaratish yoki mavjud testlarni yangilash bo'yicha yordam kerak bo'lsa, "
        "so'rashdan tortinmang! 🤗 \nBiz har doim yordamga tayyormiz! 💪 ( /help )"
    )

    # Boshlang'ich komandaga qaytish uchun yordam so'rash yoki boshqa amallarni bajarish uchun
    await start_command(msg, respond_text)

@subscripition_router.message(F.text == "👤 Kabinam")
@subscripition_router.message(Command("kabinam"))
async def view_subscription(msg: Message):
    global obuna_nomi, test_baza, yangilash
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    username = msg.from_user.username
    user_first_name = msg.from_user.first_name
    await create_user_if_not_exists(user_id=user_id, chat_id=chat_id, username=username)
    usage_type = (await get_user_by_id(user_id))[0]["usage_type"]
    # title, capacity, bank_id
    if usage_type == "ordinary":
        obuna_nomi = "Oddiy 🌱"
        test_baza, yangilash = 3, 3
    elif usage_type == "pro":
        obuna_nomi = "Super 💎"
        test_baza, yangilash = 5, 3
    elif usage_type == "founder":
        obuna_nomi = "Asoschi 👑"
        test_baza, yangilash = -1, -1

    respond = ""
    respond_text = (
        f"Salom, '<b>{user_first_name}!</b>' 👋 Sizning obuna tarifingiz <b>{obuna_nomi}</b> 😎\n\n"
        f"Mana, sizga nimalar taqdim etilmoqda: 🎉\n"
        f"✅ <code>{test_baza}</code> ta test bazasini yaratishingiz mumkin. Endi sizda ajoyib testlar yaratish imkoniyati bor! 💡\n"
        f"🔄 Har bir testni <code>{yangilash}</code> marta yangilab, ularni yanada mukammallashtirishingiz mumkin. 🚀\n\n"
        f"Qiziqarli testlar va yangiliklar kutmoqda! Agar yordam kerak bo'lsa, so'rashdan tortinmang! 🤗"
    )
    respond += respond_text

    await start_command(msg, respond)

    info = await get_info_for_view_subs(user_id)
    print("view_subs:76 \n", info)
    if info:
        await view_test_base_info(msg, user_id, info)
