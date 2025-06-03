import os
from aiogram import Bot

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


from dotenv import load_dotenv
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN")

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
