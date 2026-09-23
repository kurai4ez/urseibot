import asyncio

from database.connection import Database
from database.users import UserRepository


async def main():
    db = Database()
    await db.connect()

    users = UserRepository(db)

    user_id = 859915291 # сюда ID существующего пользователя

    group = await users.get_group(user_id)

    print("Группа пользователя:", group)

    await db.close()


asyncio.run(main())