import os
from aiogram import Bot

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

API_TOKEN = os.getenv("BOT_TOKEN", "7349199816:AAFawLSUO9jpZJuKS0VZ68SZBQ4F3qzUgLo")

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
