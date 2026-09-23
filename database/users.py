class UserRepository:
    def __init__(self, db):
        self.db = db

    async def get_group(self, user_id: int):
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT selected_group
                FROM users
                WHERE user_id = $1
                """,
                user_id
            )

            return row["selected_group"] if row else None

    async def save(
        self,
        user_id: int,
        first_name: str,
        group: str,
        username: str | None = None
    ):
        async with self.db.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (
                    user_id,
                    first_name,
                    username,
                    selected_group
                )
                VALUES ($1, $2, $3, $4)

                ON CONFLICT (user_id)
                DO UPDATE SET
                    first_name = $2,
                    username = COALESCE($3, users.username),
                    selected_group = $4,
                    updated_at = NOW()
                """,
                user_id,
                first_name,
                username,
                group
            )

    async def get_stats(self):
        async with self.db.pool.acquire() as conn:

            # Всего пользователей
            total_users = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM users
                """
            )

            # Пользователи с выбранной группой
            users_with_group = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM users
                WHERE selected_group IS NOT NULL
                """
            )

            # Пользователи без группы
            users_without_group = (
                total_users - users_with_group
            )

            # Зарегистрировались сегодня
            today_users = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM users
                WHERE created_at >= CURRENT_DATE
                """
            )

            # Зарегистрировались за последние 7 дней
            week_users = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM users
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                """
            )

            # Зарегистрировались за последние 30 дней
            month_users = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM users
                WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                """
            )

            # Самые популярные группы
            popular_groups = await conn.fetch(
                """
                SELECT
                    selected_group,
                    COUNT(*) AS user_count
                FROM users
                WHERE selected_group IS NOT NULL
                GROUP BY selected_group
                ORDER BY user_count DESC
                LIMIT 5
                """
            )
            recent_users = await conn.fetch(
                """
                SELECT
                    user_id,
                    first_name,
                    username,
                    selected_group,
                    created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT 5
                """
            )

            return {
                "total_users": total_users,
                "users_with_group": users_with_group,
                "users_without_group": users_without_group,

                "today_users": today_users,
                "week_users": week_users,
                "month_users": month_users,

                "popular_groups": [
                    (
                        row["selected_group"],
                        row["user_count"],
                    )
                    for row in popular_groups
                ],

                "recent_users": [
                    {
                        "user_id": row["user_id"],
                        "first_name": row["first_name"],
                        "username": row["username"],
                        "group": row["selected_group"],
                        "created_at": row["created_at"],
                    }
                    for row in recent_users
                ],
            }