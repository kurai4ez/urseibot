from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


ADMIN_IDS = {
    859915291,
}


@router.message(Command("stats"))
async def stats(
    message: Message,
    users,
    chats,
):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer(
            "❌ Эта команда только для администраторов."
        )
        return

    try:
        user_stats = await users.get_stats()
        chat_stats = await chats.get_stats()

        text = "📊 <b>СТАТИСТИКА БОТА</b>\n\n"

        # Пользователи

        text += "👤 <b>ПОЛЬЗОВАТЕЛИ</b>\n"

        text += (
            f"├ Всего: "
            f"<b>{user_stats['total_users']}</b>\n"
        )

        text += (
            f"├ Выбрали группу: "
            f"<b>{user_stats['users_with_group']}</b>\n"
        )

        text += (
            f"└ Без группы: "
            f"<b>{user_stats['users_without_group']}</b>\n\n"
        )

        # Чаты

        text += "💬 <b>ЧАТЫ</b>\n"

        text += (
            f"├ Всего: "
            f"<b>{chat_stats['total_chats']}</b>\n"
        )

        text += (
            f"├ Активных: "
            f"<b>{chat_stats['active_chats']}</b>\n"
        )

        text += (
            f"├ Групповых: "
            f"<b>{chat_stats['group_chats']}</b>\n"
        )

        text += (
            f"├ Супергрупп: "
            f"<b>{chat_stats['supergroup_chats']}</b>\n"
        )

        text += (
            f"├ Личных: "
            f"<b>{chat_stats['private_chats']}</b>\n"
        )

        text += (
            f"└ С группой: "
            f"<b>{chat_stats['chats_with_group']}</b>\n\n"
        )

        # Популярные группы

        text += "🏆 <b>ПОПУЛЯРНЫЕ ГРУППЫ</b>\n"

        popular_groups = user_stats[
            "popular_groups"
        ]

        if popular_groups:

            for index, (group, count) in enumerate(
                popular_groups,
                start=1,
            ):
                text += (
                    f"{index}. "
                    f"<b>{group}</b> — "
                    f"{count}\n"
                )

        else:
            text += "Пока нет данных\n"

        text += "\n📅 <b>РЕГИСТРАЦИИ</b>\n"

        text += (
            f"├ Сегодня: "
            f"<b>{user_stats['today_users']}</b>\n"
        )

        text += (
            f"├ За 7 дней: "
            f"<b>{user_stats['week_users']}</b>\n"
        )

        text += (
            f"└ За 30 дней: "
            f"<b>{user_stats['month_users']}</b>\n"
        )

        # Последние пользователи

        text += "\n🆕 <b>ПОСЛЕДНИЕ ПОЛЬЗОВАТЕЛИ</b>\n"

        recent_users = user_stats["recent_users"]

        if recent_users:
            for user in recent_users:

                username = user["username"]

                if username:
                    username_text = f"@{username}"
                else:
                    username_text = "без username"

                first_name = user["first_name"] or "Без имени"

                text += (
                    f"• <b>{first_name}</b> — "
                    f"{username_text}\n"
                )
        else:
            text += "Пока нет данных\n"

        now = datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )


        text += (
            f"\n🕐 Обновлено: "
            f"<code>{now}</code>"
        )

        await message.answer(
            text,
            parse_mode="HTML",
        )


    except Exception as e:

        print(f"❌ STATS ERROR: {type(e).__name__}: {e}")

        await message.answer(

            "❌ Ошибка получения статистики."

        )