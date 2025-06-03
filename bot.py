import os
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiohttp import web

from database import initialize_database
from database.banks import update_capacity_by_time
from core.bot_instance import bot as b
from app import all_router


dp = Dispatcher(storage=MemoryStorage())

for router in all_router:
    dp.include_router(router)

commands = [
    BotCommand(command="start", description="Botni ishga tushirish"),
    BotCommand(command="help", description="Yordam olish"),
    BotCommand(command="testlarim", description="Testlaringizni ko‘rish"),
    BotCommand(command="kabinam", description="Mening profilim"),
    BotCommand(command="test", description="Testni boshlash"),
    BotCommand(command="savollar", description="Savollarni yuklab olish"),
]

async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(commands)

# Webhook so'rovlarni qabul qilish uchun handler
async def handle_webhook(request):
    update = await request.json()
    print(update)
    await dp.feed_raw_update(bot=b, update=update)
    return web.Response(text="OK")

async def on_startup(bot: Bot, webhook_url: str):
    print(webhook_url)
    # Webhookni o'rnatish
    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )
    print(f"✅ Webhook {webhook_url} ga o'rnatildi...")

async def main():
    print("✅ Bot ishga tushdi...")
    initialize_database()  # Faqat bir marta ishlatiladi

    # Webhook sozlamalari
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST","https://fff9-94-158-58-31.ngrok-free.app")  # Railway domeningiz
    WEBHOOK_PATH = "/webhook"
    WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
    WEBAPP_HOST = "0.0.0.0"
    WEBAPP_PORT = int(os.getenv("PORT", 8080))  # Railway PORT ni muhit o'zgaruvchisidan oladi

    # Bot komandalarini o'rnatish
    await set_bot_commands(b)

    # aiohttp serverini sozlash
    app = web.Application()
    app.add_routes([web.post(WEBHOOK_PATH, handle_webhook)])

    # Webhookni o'rnatish
    await on_startup(b, WEBHOOK_URL)

    # Serverni ishga tushirish
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()

    print(f"✅ Server {WEBAPP_HOST}:{WEBAPP_PORT} da ishlamoqda...")
    # Server doimiy ishlashi uchun cheksiz kutish
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
