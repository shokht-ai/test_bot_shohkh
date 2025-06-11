import os
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiohttp import web
from dotenv import load_dotenv

from database import initialize_database
from core.bot_instance import bot as b
from app import all_router

# === Logging konfiguratsiyasi ===
LOG_FILE = "bot.log"

# Logger sozlash
logger = logging.getLogger(__name__)
logger.disabled = True
logger.setLevel(logging.DEBUG)

# Log formatini aniqlash
log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

# # Faylga yozish uchun handler (lokal ishlatish uchun)
# file_handler = logging.FileHandler(LOG_FILE, mode='w')
# file_handler.setFormatter(log_format)
# logger.addHandler(file_handler)

# stdout’ga chiqarish uchun handler (Railway va terminal uchun)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
logger.addHandler(stream_handler)


# === Muhit o‘zgaruvchilarini yuklash ===
load_dotenv()

# === Dispatcher va routerlar ===
dp = Dispatcher(storage=MemoryStorage())

for router in all_router:
    dp.include_router(router)

# === Bot komandalar ro'yxati ===
commands = [
    BotCommand(command="start", description="Botni ishga tushirish"),
    BotCommand(command="help", description="Yordam olish"),
    BotCommand(command="testlarim", description="Testlaringizni ko‘rish"),
    BotCommand(command="kabinam", description="Mening profilim"),
    BotCommand(command="test", description="Testni boshlash"),
    BotCommand(command="savollar", description="Savollarni yuklab olish"),
]

# === Komandalarni o‘rnatish ===
async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(commands)
    logger.info("Bot komandalar o‘rnatildi.")

# === Webhook so‘rovlarni qabul qilish ===
async def handle_webhook(request):
    update = await request.json()
    await dp.feed_raw_update(bot=b, update=update)
    return web.Response(text="OK")

# === Webhook o‘rnatish ===
async def on_startup(bot: Bot, webhook_url: str):
    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )
    logger.info(f"✅ Webhook {webhook_url} ga o‘rnatildi...")

# === Asosiy funksiya ===
async def cleanup(bot: Bot, runner_clean: web.AppRunner):
    """Clean up resources properly"""
    try:
        await bot.delete_webhook()
        await bot.session.close()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

    try:
        await runner_clean.cleanup()
    except Exception as e:
        logger.error(f"Error cleaning up runner: {e}")


async def main():
    global runner
    try:
        logger.info("✅ Bot starting...")

        await initialize_database()
        logger.info("Database connected.")

        # Webhook settings
        WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "YOUR_DOMAIN")
        WEBHOOK_PATH = "/webhook"
        WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
        WEBAPP_HOST = "0.0.0.0"
        WEBAPP_PORT = int(os.getenv("PORT", 8080))

        await set_bot_commands(b)

        app = web.Application()
        app.add_routes([web.post(WEBHOOK_PATH, handle_webhook)])

        await on_startup(b, WEBHOOK_URL)

        runner = web.AppRunner(app)
        await runner.setup()

        try:
            site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
            await site.start()
            logger.info(f"✅ Server running on {WEBAPP_HOST}:{WEBAPP_PORT}")
            await asyncio.Event().wait()

        except OSError as e:
            if e.errno == 98:  # Address already in use
                logger.error(f"Port {WEBAPP_PORT} is already in use. Please choose another port.")
                raise
            else:
                logger.error(f"Server error: {e}")
                raise

    except asyncio.CancelledError:
        logger.info("Bot shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Cleaning up resources...")
        await cleanup(b, runner)
        logger.info("✅ Bot shut down successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")