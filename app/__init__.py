# from app.handlers import base_handler_router, file_handler_router
# from app.uploading_file import uploading_file_router
# from app.view_subscription_price import subscripition_router
# from app.generate_pro_keys import pro_key_router
# from app.stats import stats_router
# from app.start_poll import start_poll_router
# from app.sending_file import sending_file_router
#
# all_routers = [
#     base_handler_router,
#     uploading_file_router,
#     subscripition_router,
#     pro_key_router,
#     start_poll_router,
#     stats_router,
#     sending_file_router,
#     file_handler_router,
# ]


from aiogram import Router
from aiogram.types import Message

vaqtinchalik = Router()
all_router = [vaqtinchalik,]

@vaqtinchalik.message()
async def tarmoqda(msg:Message):
    await msg.answer("""
    🛑 Bot faoliyati vaqtincha to‘xtatildi 🛠️

Hurmatli foydalanuvchilar!
Texnik sabablarga ko‘ra botimizning ishlashi hozircha to‘liq to‘xtatilganini ma’lum qilamiz. ⛔️

🔧 Hozirda muammolarni bartaraf etish ustida ish olib borilmoqda.
🕒 Qayta ishga tushirish muddati hozircha noma’lum, ammo bu haqda albatta qo‘shimcha ma’lumot beramiz.

Noqulayliklar uchun uzr so‘raymiz 🙏
Sizning sabr-toqatingiz va tushunishingiz uchun katta rahmat! ❤️

Hurmat bilan,
Bot jamoasi 🤖
    """)




