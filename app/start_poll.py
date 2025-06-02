from asyncio import sleep
from random import sample

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, Message


from app.handlers.base_handler import start_command
from core.bot_instance import bot
from database.questions import get_questions_by_bank

start_polling_router = Router()


class TestState(StatesGroup):
    choosing_question = State()
    checking_answer = State()


# ✅ Yordamchi funksiya: Tasodifiy savollarni olish
async def fetch_random_questions(bank_id: int, limit: int = 15) -> list:
    """
    Berilgan bank_id bo‘yicha savollarni bazadan olib, maksimal 30 tasodifiy savolni tanlab qaytaradi.

    :param bank_id:
    :param limit:
    :return: savollar to'plami
    """
    questions = get_questions_by_bank(bank_id)
    if not questions:
        return []
    return sample(questions, min(limit, len(questions)))


# ✅ Yordamchi funksiya: Poll uchun ma'lumot tayyorlash
def prepare_poll_data(question: tuple) -> tuple:
    """
    Bitta savolni (tuple formatida) oladi va:
        Savol matnini (question_text)

        Tasodifiy tartibda javob variantlari

        To‘g‘ri javobning yangi indeksini tayyorlab beradi.

    :param question:
    :return: quiz test tuzish uchun ma'lumotlar
    """

    correct_answer = question[1]
    options = [question[1], question[2], question[3], question[4]]
    randomized_options = sample(options, 4)
    correct_index = randomized_options.index(correct_answer)
    return question[0], randomized_options, correct_index


# ✅ Yordamchi funksiya: Test holatini boshlang'ichga sozlash
async def reset_test_state(state: FSMContext, questions: list, chat_id: int, message_id: int, bank_id: int, the_number: int):
    """
    Testni boshlash uchun kerakli holatlarni (FSM holati) noldan sozlaydi:
        Savollar, indeks, statistikalar (to‘g‘ri/noto‘g‘ri/javobsiz)

        Chat va message ID, bank ID

    :param the_number:
    :param state:
    :param questions:
    :param chat_id:
    :param message_id:
    :param bank_id:
    :return: None
    """
    await state.update_data({
        "questions": questions,
        "index": 0,
        "correct": 0,
        "incorrect": 0,
        "unanswered": 0,
        "answered": False,
        "correct_option_id": None,
        "chat_id": chat_id,
        "message_id": message_id,
        "bank_id": bank_id,
        "number_of_test": the_number
    })


# ✅ Yordamchi funksiya: Test yakunida natija yuborish
async def send_test_summary(chat_id: int, data: dict, state: FSMContext):
    """
    Keyingi savolni poll shaklida yuboradi:
        15 soniyalik javob berish imkoniyati

        Javob bo‘lmasa, “javobsiz” deb belgilanadi

        Har bir polldan so‘ng avtomatik navbatdagi savol yuboriladi

    :param state:
    :param chat_id:
    :param data:
    :return:
    """
    summary = (
        "✅ <b>Test yakuni</b> ✅\n\n"
        f"To‘g‘ri javoblar: <code>{data.get('correct', 0)}</code>\n"
        f"Noto‘g‘ri javoblar: <code>{data.get('incorrect', 0)}</code>\n"
        f"Javob berilmagan: <code>{data.get('unanswered', 0)}</code>"
    )
    await state.clear()
    await bot.send_message(chat_id, summary)


# ✅ Test davomida to‘xtatish tugmasi
def stop_test_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⛔ Testni to‘xtatish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@start_polling_router.message(F.text =="⛔ Testni to‘xtatish")
async def stop_test(message: Message, state: FSMContext):
    data = await state.get_data()
    if int(data.get("number_of_test", 0)) - 1 != int(data.get("index", 0)):
        await state.update_data(unanswered=(int(data.get("number_of_test", 0)) - int(data.get("index", 0))))
    data = await state.get_data()
    await send_test_summary(message.chat.id, data, state)
    await start_command(message, text="✅ Test to'xtatildi! Siz bosh sahifaga qaytdingiz.")


# ✅ Asosiy funksiya: Keyingi savolni yuborish
async def send_next_poll(msg: Message, state: FSMContext):
    """
        Test yakunida foydalanuvchiga:
        To‘g‘ri javoblar soni

        Noto‘g‘ri javoblar soni

        Javob berilmagan savollar soni ko‘rinishida yakuniy natijani yuboradi.

    :param msg:
    :param state:
    :return:
    """
    chat_id = msg.chat.id
    data = await state.get_data()
    questions = data.get("questions", [])
    poll_index = data.get("index", 0)
    if (poll_index >= len(questions) or len(data) == 0) and len(questions) != 0:
        await stop_test(msg, state)
        return
    elif len(questions) == 0:
        return
    question = questions[poll_index]
    question_text, options, correct_index = prepare_poll_data(question)
    question_text = f"[{poll_index + 1}/{data.get("number_of_test", '')}] " + question_text
    poll_msg = await bot.send_poll(
        chat_id=chat_id,
        question=question_text,
        options=options,
        type="quiz",
        correct_option_id=correct_index,
        is_anonymous=False,
        open_period=15,
        reply_markup=stop_test_keyboard()
    )

    await state.update_data(
        poll_msg_id=poll_msg.message_id,
        correct_option_id=correct_index
    )

    # 15 soniya kutamiz, javob kelmasa javob berilmagan deb hisoblaymiz
    timer = 15
    while timer > 0:
        updated_data = await state.get_data()
        if updated_data.get("answered", False):
            break
        await sleep(1)
        timer -= 1
    updated_data = await state.get_data()
    if not updated_data.get("answered", False):
        await state.update_data(unanswered=updated_data.get("unanswered", 0) + 1)

    await state.update_data(
        index=poll_index + 1,
        answered=False
    )
    await send_next_poll(msg, state)


# ✅ Testni boshlash (callback orqali)
@start_polling_router.callback_query(lambda c: c.data.startswith("test:"))
async def start_poll_test(callback: CallbackQuery, state: FSMContext):
    """
    Inline tugma orqali test boshlanadi. Callback data dan bank_id ni oladi, savollarni tayyorlaydi va send_next_poll orqali testni ishga tushiradi.

    :param callback:
    :param state:
    :return:
    """
    await callback.answer()
    parts = callback.data.split(":")
    if len(parts) != 2 or not parts[1].isdigit():
        await callback.answer("❌ Noto‘g‘ri format.", show_alert=True)
        return

    bank_id = int(parts[1])
    questions = await fetch_random_questions(bank_id)

    if not questions:
        await callback.message.answer("❌ Bu bankda savollar yo‘q.")
        return

    await reset_test_state(
        state,
        questions,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        bank_id=bank_id,
        the_number=len(questions)
    )

    await send_next_poll(callback.message, state)


# ✅ Foydalanuvchi javobini qayta ishlash
@start_polling_router.poll_answer()
async def poll_answer_handler(poll_answer: types.PollAnswer, state: FSMContext):
    data = await state.get_data()
    correct_option_id = data.get("correct_option_id")

    if poll_answer.option_ids and poll_answer.option_ids[0] == correct_option_id:
        await state.update_data(correct=data.get("correct", 0) + 1)
    else:
        await state.update_data(incorrect=data.get("incorrect", 0) + 1)

    await state.update_data(answered=True)
