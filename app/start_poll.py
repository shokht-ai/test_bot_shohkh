# import logging
from asyncio import sleep
from random import sample

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardButton, \
    InlineKeyboardMarkup

from app.handlers.base_handler import start_command
from core.bot_instance import bot
from database.questions import get_questions_by_bank


# # Logger sozlash
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

start_poll_router = Router()


class TestState(StatesGroup):
    choosing_question = State()
    checking_answer = State()


# ✅ Yordamchi funksiya: Tasodifiy savollarni olish
async def fetch_random_questions(bank_id: int, limit: int = 15) -> list[dict]:
    """
    Berilgan bank_id bo‘yicha savollarni bazadan olib, maksimal 30 tasodifiy savolni tanlab qaytaradi.

    :param bank_id:
    :param limit:
    :return: savollar to'plami
    """
    # question, correct, wrong1, wrong2, wrong3
    records = await get_questions_by_bank(bank_id)
    if not records:
        return []
    questions = [dict(q) for q in records]
    return sample(questions, min(limit, len(questions)))


# ✅ Yordamchi funksiya: Poll uchun ma'lumot tayyorlash
def prepare_poll_data(question: dict) -> tuple:
    """
    Bitta savolni dict formatida oladi va:
        - Savol matni (question_text)
        - Tasodifiy tartibda javob variantlari
        - To‘g‘ri javobning yangi indeksini qaytaradi
    """
    correct_answer = question["correct"]
    options = [
        question["correct"],
        question["wrong1"],
        question["wrong2"],
        question["wrong3"]
    ]
    randomized_options = sample(options, 4)
    correct_index = randomized_options.index(correct_answer)
    return question["question"], randomized_options, correct_index


# ✅ Yordamchi funksiya: Test holatini boshlang'ichga sozlash
async def reset_test_state(state: FSMContext, questions: list, chat_id: int, message_id: int, bank_id: int,
                           the_number: int, callback_poll: str):
    """
    Testni boshlash uchun kerakli holatlarni (FSM holati) noldan sozlaydi:
        Savollar, indeks, statistikalar (to‘g‘ri/noto‘g‘ri/javobsiz)

        Chat va message ID, bank ID

    :param callback_poll
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
        "number_of_test": the_number,
        "callback_poll": callback_poll,
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
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Testni qayta boshlash",
                    callback_data=data.get("callback_poll")
                )
            ]
        ]
    )
    await state.clear()
    # Qayta boshlash tugmasi
    await bot.send_message(chat_id, summary, reply_markup=keyboard)

# ✅ Test davomida to‘xtatish tugmasi
def stop_test_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⛔ Testni to‘xtatish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


@start_poll_router.message(F.text == "⛔ Testni to‘xtatish")
async def stop_test(message: Message, state: FSMContext):
    try:
        data = await state.get_data()

        # Javob berilmagan savollarni hisoblash
        unanswered = int(data.get("number_of_test", 0)) - int(data.get("index", 0))
        await state.update_data(
            unanswered=unanswered,
            force_stop = True if message.text == "⛔ Testni to‘xtatish" else False
        )


        # Yangi ma'lumotlarni olish
        data = await state.get_data()

        # Avvalgi pollni to'xtatish
        if not "test_finished" in data:#  or data["force_stop"]:
            try:
                await bot.stop_poll(message.chat.id, data['poll_msg_id'])
            except Exception as e:
                print(f"Pollni to'xtatishda xato: {e}")

        text = "✅ Test to'xtatildi! Siz bosh sahifaga qaytdingiz."
        text += "\nIltimos, yuqoridagi test rasman tugaguncha kutib tursangiz." if data['force_stop'] else ""
        # Natijani yuborish
        await send_test_summary(
            chat_id=message.chat.id,
            data=data,
            state=state
        )
        await start_command(message, text)
    except Exception as e:
        print(f"start_poll::stop_test da xatolik\n{e}")

# ✅ Asosiy funksiya: Keyingi savolni yuborish
async def send_next_poll(msg: Message, state: FSMContext):
    global updated_data
    chat_id = msg.chat.id
    data = await state.get_data()
    questions = data.get("questions", [])
    poll_index = data.get("index", 0)

    # Test yakuniga tekshirish (avvalgi versiyada bor)
    if (poll_index >= len(questions) or len(data) == 0) and len(questions) != 0:
        await state.update_data(test_finished=True)
        await stop_test(msg, state)
        return
    elif len(questions) == 0:
        return

    question = questions[poll_index]
    question_text, options, correct_index = prepare_poll_data(question)
    question_text = f"[{poll_index + 1}/{data.get('number_of_test', '')}] " + question_text

    try:
        # Yangi poll yuborish
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
        # Poll message_id ni stateda saqlash (MUHIM QO'SHIMCHA)
        await state.update_data(
            poll_msg_id=poll_msg.message_id,
            correct_option_id=correct_index
        )

        # 15 soniya kutish davri
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

        # Keyingi savolga o'tish
        await send_next_poll(msg, state)

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        await state.update_data(unanswered=updated_data.get("unanswered", 0) + 1)
        await send_next_poll(msg, state)


# ✅ Testni boshlash (callback orqali)
@start_poll_router.callback_query(lambda c: c.data.startswith("test:"))
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
        the_number=len(questions),
        callback_poll=callback.data,
    )

    await send_next_poll(callback.message, state)


# ✅ Foydalanuvchi javobini qayta ishlash
@start_poll_router.poll_answer()
async def poll_answer_handler(poll_answer: types.PollAnswer, state: FSMContext):
    data = await state.get_data()
    correct_option_id = data.get("correct_option_id")

    if poll_answer.option_ids and poll_answer.option_ids[0] == correct_option_id:
        await state.update_data(correct=data.get("correct", 0) + 1)
    else:
        await state.update_data(incorrect=data.get("incorrect", 0) + 1)

    await state.update_data(answered=True)
