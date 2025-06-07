from aiogram import types, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from database.users import create_user_if_not_exists
base_handler_router =Router()

# /start komandasi uchun handler
@base_handler_router.message(Command("start"))
async def start_command(message: types.Message, text = ""):
    check = False
    if len(text) == 0:
        check = True
        text = (
            "👋 Salom!\n\n"
            "Bu bot — test savollaringizni avtomatik *quiz test*ga aylantiradi!\n\n"
            "✅ Excel (.xlsx) fayl yuboring. Har bir qator quyidagicha bo‘lishi kerak:\n"
            "`Savol | To‘g‘ri javob | Noto‘g‘ri javob | Noto‘g‘ri javob | Noto‘g‘ri javob`\n\n"
            "⚠️ Agar biror ustun bo‘sh qolsa, o‘sha qator o‘tkazib yuboriladi.\n\n"
            "📎 Quyida namunaviy faylni ko‘rib chiqing va shunga o‘xshatib tayyorlang."
        )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Testlarim"), KeyboardButton(text="👤 Kabinam")],
            [KeyboardButton(text="🚀 Testni boshlash")],
            [KeyboardButton(text="📥 Savollarni yuklab olish")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        text,
        reply_markup=keyboard
    )
    if check:
        await message.answer_document(document=FSInputFile("Namuna_fayl/Namuna.xlsx"),caption="Iltimos, fayldan foydalaning! 😊📂")
    username = message.from_user.username or ""
    await create_user_if_not_exists(message.from_user.id, message.chat.id, username)

# /help komandasi uchun
@base_handler_router.message(Command('help'))
async def help_command(message: types.Message):
    await message.answer(
        "🛠 <b>Yordam oynasi</b>\n\n"
        "Quyidagi komandalar orqali bot imkoniyatlaridan foydalanishingiz mumkin:\n\n"
        "<b>/start</b> – Botni ishga tushirish 🚀\n"
        "<b>/help</b> – Yordam oynasini ko‘rsatish ❓\n"
        "<b>/testlarim</b> – Saqlangan testlaringizni ko‘rish 📚\n"
        "<b>/kabinam</b> – Profil va obuna tafsilotlari 🎖\n"
        "<b>/test</b> – Testni boshlash 📝\n"
        "<b>/savollar</b> – Savollar faylini yuklab olish 📥\n\n"
        "📌 Yoki quyidagi menyudan foydalaning — tanlash osonroq! 😊"
    )
    await message.answer(
        f"📌 <b>Faylni yangilash uchun:</b>\n"
        f"Yangi fayl yuborayotganda, <b>Izoh</b> qismiga eski faylning <b><code>ID</code></b> sini yozing.\n\n"
        f"✅ Aks holda, fayl yangi deb saqlanadi."
    )
    if message.from_user.id == 7895477080:
        text = (
            "<b>🔑 Asoschi</b> uchun yashirin buyruqlar:\n\n"
            "<b>/pro</b> - Obuna tarifini yaratish uchun maxfiy kalitni hosil qiladi. \n"
            "          Shu kalitni <code>/pro (kalit)</code> ko‘rinishida botga yuboring. 🔑\n\n"
            "<b>/info_bot</b> - Botning foydalanuvchilari va statistikasi haqida batafsil ma’lumot beradi. 📊\n\n"
            "<b>/start_users</b> - Foydalanuvchi tarifini 'Oddiy' ga o'tqazish\n"
            "           <code>/start_users (User_id)</code> Foydalanuvchi telegram ID sini yuboring.\n\n"
            "<b>/update_capacity</b> - Barcha foydalanuvchilarning faylni qayta yangilash imkoniyatlarini yangilaydi."
        )

        await message.answer(text)

def register_base_handlers(dp: Dispatcher):
    dp.message.register(start_command, CommandStart())
    dp.message.register(help_command, Command("help"))
