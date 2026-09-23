from io import BytesIO
import asyncio
import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from parsers.groups import GROUPS
from parsers.parser import get_weeks
from pillow import create_schedule_image


router = Router()

# ============================================================
# RATE LIMIT
# ============================================================

RATE_LIMIT = 5  # секунд

_last_schedule_request = {}


def is_rate_limited(message: Message) -> bool:
    if message.chat.type == "private":
        key = f"user:{message.from_user.id}"
    else:
        key = f"chat:{message.chat.id}"

    now = time.monotonic()

    last_request = _last_schedule_request.get(key)

    if last_request is not None:
        elapsed = now - last_request

        if elapsed < RATE_LIMIT:
            return True

    _last_schedule_request[key] = now

    return False

# ============================================================
# ПОЛУЧЕНИЕ РАСПИСАНИЯ
# ============================================================

async def get_user_schedule(
    message: Message,
    users,
    chats,
    next_week: bool = False,
):

    if message.chat.type == "private":
        group = await users.get_group(
            message.from_user.id
        )
    else:
        group = await chats.get_group(
            message.chat.id
        )

    if not group:
        return (
            None,
            None,
            "❌ Сначала выбери группу через /setgr"
        )

    group_id = GROUPS.get(group)

    if not group_id:
        return (
            None,
            None,
            "❌ Не удалось найти ID этой группы"
        )

    # Получаем расписание с таймаутом 10 секунд
    try:

        current_week, next_week_schedule = (
            await asyncio.wait_for(
                asyncio.to_thread(
                    get_weeks,
                    group_id,
                ),
                timeout=10,
            )
        )

    except asyncio.TimeoutError:

        return (
            None,
            None,
            "❌ Не удалось получить расписание за 10 секунд."
        )

    except Exception as e:

        print(
            f"Ошибка получения расписания "
            f"для {group}: {e}"
        )

        return (
            None,
            None,
            "❌ Не удалось получить расписание."
        )

    schedule = (
        next_week_schedule
        if next_week
        else current_week
    )

    if not schedule:
        return (
            None,
            None,
            "❌ Расписание на эту неделю не найдено"
        )

    return group, schedule, None


# ============================================================
# ОТПРАВКА РАСПИСАНИЯ
# ============================================================

async def send_schedule(
    message: Message,
    users,
    chats,
    next_week: bool = False,
):

    # --------------------------------------------------------
    # АНТИСПАМ
    # --------------------------------------------------------

    if is_rate_limited(message):

        await message.answer(
            "не спамь"
        )

        return

    # --------------------------------------------------------
    # ПОЛУЧАЕМ РАСПИСАНИЕ
    # --------------------------------------------------------

    group, schedule, error = await get_user_schedule(
        message=message,
        users=users,
        chats=chats,
        next_week=next_week,
    )

    if error:
        await message.answer(error)
        return

    # --------------------------------------------------------
    # СОЗДАЁМ ИЗОБРАЖЕНИЕ
    # --------------------------------------------------------

    title = (
        f"Следующая неделя • {group}"
        if next_week
        else f"Текущая неделя • {group}"
    )

    try:

        image = create_schedule_image(
            schedule=schedule,
            title=title,
        )

    except Exception as e:

        print(
            f"Ошибка генерации изображения "
            f"для {group}: {e}"
        )

        await message.answer(
            "❌ Не удалось создать расписание."
        )

        return

    # --------------------------------------------------------
    # IMAGE → BYTES
    # --------------------------------------------------------

    photo = BytesIO()

    try:

        image.save(
            photo,
            format="PNG",
            optimize=True,
        )

        photo.seek(0)

        photo_file = BufferedInputFile(
            photo.read(),
            filename="schedule.png",
        )

    finally:

        image.close()
        photo.close()

    # --------------------------------------------------------
    # ОТПРАВКА
    # --------------------------------------------------------

    try:

        await message.answer_photo(
            photo=photo_file,
        )

    except Exception as e:

        print(
            f"Ошибка отправки расписания "
            f"для {group}: {e}"
        )

        await message.answer(
            "❌ Не удалось отправить расписание."
        )


# ============================================================
# /WEEK
# ============================================================

@router.message(Command("week"))
async def week(
    message: Message,
    users,
    chats,
):
    """
    Текущая неделя.
    """

    await send_schedule(
        message=message,
        users=users,
        chats=chats,
        next_week=False,
    )


# ============================================================
# /NEXT
# ============================================================

@router.message(Command("next"))
async def next_week(
    message: Message,
    users,
    chats,
):
    """
    Следующая неделя.
    """

    await send_schedule(
        message=message,
        users=users,
        chats=chats,
        next_week=True,
    )


# ============================================================
# /BELLS
# ============================================================

@router.message(Command("bells"))
async def bells_handler(
    message: Message,
):
    """
    Расписание звонков.
    """

    await message.answer_photo(
        photo="https://ibb.co/S40cj46y"
    )

@router.message(Command('teacher'))
async def teacher_handler(message: Message):
    await message.answer('Временно недоступно')