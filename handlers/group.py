from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from parsers.groups import GROUPS

router = Router()


def get_groups_by_course(course: int):
    """
    Возвращает группы указанного курса.

    Например:
    course=2
    → БДД-201
    → ИД-202
    → ИСПД-203
    """

    result = []

    for group in GROUPS:
        try:
            group_number = group.split("-")[-1]
            group_course = int(group_number[0])

            if group_course == course:
                result.append(group)

        except (ValueError, IndexError):
            continue

    return result


def courses_keyboard():
    builder = InlineKeyboardBuilder()

    for course in range(1, 5):
        builder.button(
            text=f"{course} курс",
            callback_data=f"course:{course}"
        )

    builder.adjust(2)

    return builder.as_markup()


def groups_keyboard(course: int):
    builder = InlineKeyboardBuilder()

    groups = get_groups_by_course(course)

    for group in groups:
        builder.button(
            text=group,
            callback_data=f"setgr:{group}"
        )

    builder.button(
        text="◀️ Назад",
        callback_data="courses"
    )

    builder.adjust(2)

    return builder.as_markup()


@router.message(Command("setgr"))
async def set_group_handler(message: Message):
    await message.answer(
        "📚 Выбери курс:",
        reply_markup=courses_keyboard()
    )


@router.callback_query(lambda callback: callback.data == "courses")
async def courses_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 Выбери курс:",
        reply_markup=courses_keyboard()
    )

    await callback.answer()


@router.callback_query(lambda callback: callback.data.startswith("course:"))
async def course_callback(callback: CallbackQuery):
    course = int(callback.data.split(":")[1])

    groups = get_groups_by_course(course)

    if not groups:
        await callback.answer(
            "Группы этого курса не найдены",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        f"📚 {course} курс\n\n"
        f"Выбери свою группу:",
        reply_markup=groups_keyboard(course)
    )

    await callback.answer()


@router.callback_query(lambda callback: callback.data.startswith("setgr:"))
async def set_group_callback(
        callback: CallbackQuery,
        users,
        chats
):
    group = callback.data.split(":", 1)[1]

    if group not in GROUPS:
        await callback.answer(
            "Такой группы больше нет",
            show_alert=True
        )
        return

    user = callback.from_user
    chat = callback.message.chat

    if chat.type == "private":

        await users.save(
            user_id=user.id,
            first_name=user.first_name,
            username=user.username,
            group=group
        )

    else:

        await chats.save(
            chat_id=chat.id,
            chat_type=chat.type,
            title=chat.title,
            group=group
        )

    await callback.message.edit_text(
        f"✅ Группа установлена!\n\n"
        f"📚 Группа: {group}\n\n"
        f"Теперь доступны:\n"
        f"📅 /week — текущая неделя\n"
        f"📅 /next — следующая неделя"
    )

    await callback.answer()