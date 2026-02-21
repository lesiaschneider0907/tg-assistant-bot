from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.services.db import get_or_create_user

router = Router()  # роутер — группирует хендлеры этого модуля


# обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await get_or_create_user(message.from_user.id)  # регистрируем пользователя
    await message.answer(
        f"Привет! 👋\n"
        f"Я твой завхоз.\n\n"
        f"Что умею:\n"
        f"📅 Вести календарь задач\n"
        f"📁 Хранить заметки и файлы\n\n"
        f"Пока в разработке, скоро будет больше функций!"
    )