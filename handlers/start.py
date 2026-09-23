from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


router = Router()


@router.message(CommandStart())
async def start_handler(
    message: Message,
    users,
):
    group = await users.get_group(message.from_user.id)

    if group:
        await message.answer(
            f"👋 \n\n"
            f"Твоя группа: {group}\n\n"
            f"📅 /week — текущая неделя\n"
            f"📅 /next — следующая неделя\n"
            f"🔔 /bells — расписание звонков\n"
            f"👨‍🏫 /teacher — расписание преподавателя\n"
            f"⚙️ /setgr — сменить группу"
        )

    else:
        await message.answer(
            f"👋 {message.from_user.first_name}!\n\n"
            f"Используй /setgr, чтобы выбрать свою группу."
        )