import os

import asyncpg
from dotenv import load_dotenv


load_dotenv()


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "postgres"),
            ssl=os.getenv("DB_SSL", "require"),
            min_size=1,
            max_size=5,
            statement_cache_size=0,
        )

        print("✅ Подключение к БД успешно")

    async def close(self):
        if self.pool:
            await self.pool.close()
            print("🔌 БД закрыта")