class ChatRepository:
    def __init__(self, db):
        self.db = db

    async def get_group(self, chat_id: int):
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT selected_group
                FROM chats
                WHERE chat_id = $1
                  AND is_active = TRUE
                """,
                chat_id
            )

            return row["selected_group"] if row else None

    async def save(
        self,
        chat_id: int,
        chat_type: str,
        group: str,
        title: str | None = None,
    ):
        async with self.db.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO chats (
                    chat_id,
                    chat_type,
                    title,
                    selected_group,
                    is_active
                )
                VALUES ($1, $2, $3, $4, TRUE)

                ON CONFLICT (chat_id)
                DO UPDATE SET
                    chat_type = $2,
                    title = $3,
                    selected_group = $4,
                    is_active = TRUE,
                    updated_at = NOW()
                """,
                chat_id,
                chat_type,
                title,
                group,
            )

    async def get_stats(self):
        async with self.db.pool.acquire() as conn:

            # Всего чатов
            total_chats = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chats
                """
            )

            # Активные чаты
            active_chats = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chats
                WHERE is_active = TRUE
                """
            )

            # Личные чаты
            private_chats = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chats
                WHERE chat_type = 'private'
                """
            )

            # Группы
            group_chats = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chats
                WHERE chat_type = 'group'
                """
            )

            # Супергруппы
            supergroup_chats = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chats
                WHERE chat_type = 'supergroup'
                """
            )

            # Чаты с выбранной группой
            chats_with_group = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chats
                WHERE selected_group IS NOT NULL
                """
            )

            # Новые чаты за сегодня
            today_chats = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chats
                WHERE created_at >= CURRENT_DATE
                """
            )

            # Новые чаты за 7 дней
            week_chats = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chats
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                """
            )

            # Новые чаты за 30 дней
            month_chats = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chats
                WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                """
            )

            # Популярные группы среди чатов
            popular_groups = await conn.fetch(
                """
                SELECT
                    selected_group,
                    COUNT(*) AS chat_count
                FROM chats
                WHERE selected_group IS NOT NULL
                GROUP BY selected_group
                ORDER BY chat_count DESC
                LIMIT 5
                """
            )

            return {
                "total_chats": total_chats,
                "active_chats": active_chats,

                "private_chats": private_chats,
                "group_chats": group_chats,
                "supergroup_chats": supergroup_chats,

                "chats_with_group": chats_with_group,

                "today_chats": today_chats,
                "week_chats": week_chats,
                "month_chats": month_chats,

                "popular_groups": [
                    (
                        row["selected_group"],
                        row["chat_count"],
                    )
                    for row in popular_groups
                ],
            }