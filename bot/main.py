import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

from bot.handlers import start, calendar

load_dotenv()  # загружает переменные из .env файла

BOT_TOKEN = os.getenv("BOT_TOKEN")  # читает токен из переменных окружения

logger = logging.getLogger(__name__)  # логгер для этого модуля


async def main():
    # настройка формата логов
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    from bot.services.db import init_db, close_db

    # создаём экземпляр бота с HTML разметкой по умолчанию
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()  # диспетчер — маршрутизирует сообщения к нужным хендлерам

    dp.include_router(start.router)  # подключаем роутер с хендлерами /start
    dp.include_router(calendar.router)

    await init_db()  # инициализируем пул подключений к БД
    logger.info("Bot started")
    try:
        await dp.start_polling(bot)  # запускаем получение обновлений от Telegram
    finally:
        await close_db()  # закрываем соединения с БД при остановке


if __name__ == "__main__":
    asyncio.run(main())  # точка входа