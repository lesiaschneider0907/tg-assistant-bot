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
    

async def add_task(user_id: int, text: str, date, time, is_urgent: bool) -> dict:
    # добавляем задачу в календарь
    async with pool.acquire() as conn:
        task = await conn.fetchrow(
            """INSERT INTO calendar (user_id, text, date, time, is_urgent)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *""",
            user_id, text, date, time, is_urgent
        )
        return dict(task)


async def get_tasks(user_id: int, only_active: bool = False) -> list:
    # получаем задачи пользователя
    async with pool.acquire() as conn:
        if only_active:
            rows = await conn.fetch(
                """SELECT * FROM calendar WHERE user_id = $1 AND status != 2
                ORDER BY is_urgent DESC, date ASC""",
                user_id
            )
        else:
            rows = await conn.fetch(
                """SELECT * FROM calendar WHERE user_id = $1
                ORDER BY is_urgent DESC, date ASC""",
                user_id
            )
        return [dict(r) for r in rows]


async def update_task_status(user_id: int, cal_id: int, status: int) -> dict:
    # меняем статус задачи, проверяем что задача принадлежит этому пользователю
    async with pool.acquire() as conn:
        task = await conn.fetchrow(
            """UPDATE calendar SET status = $1
            WHERE cal_id = $2 AND user_id = $3
            RETURNING *""",
            status, cal_id, user_id
        )
        return dict(task) if task else None
    

async def delete_task(user_id: int, cal_id: int) -> bool:
    # удаляем задачу, проверяем что принадлежит этому пользователю
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM calendar WHERE cal_id = $1 AND user_id = $2",
            cal_id, user_id
        )
        return result == "DELETE 1"