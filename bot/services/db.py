import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# параметры подключения к БД из переменных окружения
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

pool = None  # глобальный пул соединений


async def init_db():
    # создаём пул соединений при старте бота
    global pool
    pool = await asyncpg.create_pool(**DB_CONFIG)


async def close_db():
    # закрываем пул при остановке бота
    global pool
    if pool:
        await pool.close()


async def get_or_create_user(tg_id: int) -> dict:
    # ищем пользователя в БД, если нет — создаём
    async with pool.acquire() as conn:  # берём соединение из пула
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE tg_id = $1", tg_id
        )
        if not user:
            user = await conn.fetchrow(
                """INSERT INTO users (tg_id) 
                VALUES ($1) 
                RETURNING *""",
                tg_id
            )
        return dict(user)