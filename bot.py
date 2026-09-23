import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from database.connection import Database
from database.users import UserRepository
from database.chats import ChatRepository

from handlers.start import router as start_router
from handlers.group import router as group_router
from handlers.schedule import router as schedule_router
from handlers.stats import router as stats_router

load_dotenv()


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # Подключаем БД
    db = Database()
    await db.connect()

    # Создаём репозитории
    users = UserRepository(db)
    chats = ChatRepository(db)

    # Подключаем handlers
    dp.include_router(start_router)
    dp.include_router(group_router)
    dp.include_router(schedule_router)
    dp.include_router(stats_router)

    print("🤖 Бот запущен")

    try:
        await dp.start_polling(
            bot,
            users=users,
            chats=chats,
        )

    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())