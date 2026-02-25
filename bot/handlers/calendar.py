from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime
from aiogram.filters import Filter
from aiogram import F
import re
from bot.services.db import get_or_create_user, add_task, get_tasks, update_task_status, delete_task
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

router = Router()


@router.message(Command("add"))
async def cmd_add(message: Message):
    # /add купить молоко | 2026-03-01 | 10:00
    # /add срочно сдать отчёт | 2026-03-05
    args = message.text.replace("/add", "").strip()

    if not args:
        await message.answer(
            "Формат: <code>/add текст задачи | дата | время (необязательно)</code>\n\n"
            "Примеры:\n"
            "<code>/add купить молоко | 2026-03-01</code>\n"
            "<code>/add срочно сдать отчёт | 2026-03-05 | 10:00</code>"
        )
        return

    parts = [p.strip() for p in args.split("|")]

    if len(parts) < 2:
        await message.answer("Укажи хотя бы текст и дату через <code>|</code>")
        return

    text = parts[0]
    is_urgent = any(word in text.lower() for word in ["срочно", "срочная", "urgent", "asap"])

    try:
        date = datetime.strptime(parts[1], "%Y-%m-%d").date()
    except ValueError:
        await message.answer("Дата в формате <code>ГГГГ-ММ-ДД</code>, например <code>2026-03-01</code>")
        return

    time = None
    if len(parts) >= 3:
        try:
            time = datetime.strptime(parts[2], "%H:%M").time()
        except ValueError:
            await message.answer("Время в формате <code>ЧЧ:ММ</code>, например <code>10:00</code>")
            return

    user = await get_or_create_user(message.from_user.id)
    task = await add_task(user["user_id"], text, date, time, is_urgent)

    urgent_mark = "🔴 Срочно\n" if is_urgent else ""
    time_str = f" в {time.strftime('%H:%M')}" if time else ""

    await message.answer(
        f"✅ Задача добавлена!\n\n"
        f"{urgent_mark}"
        f"📝 {task['text']}\n"
        f"📅 {date.strftime('%d.%m.%Y')}{time_str}"
    )


@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    user = await get_or_create_user(message.from_user.id)
    tasks = await get_tasks(user["user_id"])

    if not tasks:
        await message.answer("Задач пока нет 🎉")
        return

    status_emoji = {0: "⬜", 1: "🔄", 2: "✅"}
    status_text = {0: "не начато", 1: "начато", 2: "готово"}

    text = "📋 <b>Все задачи:</b>\n\n"
    for task in tasks:
        urgent = "🔴 " if task["is_urgent"] else ""
        time_str = f" {task['time'].strftime('%H:%M')}" if task["time"] else ""
        text += (
            f"{status_emoji[task['status']]} {urgent}<b>{task['text']}</b>\n"
            f"    📅 {task['date'].strftime('%d.%m.%Y')}{time_str} — {status_text[task['status']]}\n"
            f"    /done_{task['cal_id']} /started_{task['cal_id']} /not_started_{task['cal_id']} /delete_{task['cal_id']}\n\n"
        )

    await message.answer(text)


@router.message(F.text.regexp(r"^/done_\d+$"))
async def cmd_done(message: Message):
    cal_id = int(message.text.split("_")[-1])
    user = await get_or_create_user(message.from_user.id)
    task = await update_task_status(user["user_id"], cal_id, 2)
    if task:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🗑 Удалить", callback_data=DeleteCallback(cal_id=cal_id).pack()),
            InlineKeyboardButton(text="📁 Оставить", callback_data="cancel")
        ]])
        await message.answer(
            f"✅ Задача <b>{task['text']}</b> готова!\nУдалить её?",
            reply_markup=keyboard
        )
    else:
        await message.answer("Задача не найдена")


@router.message(F.text.regexp(r"^/started_\d+$"))
async def cmd_start_task(message: Message):
    cal_id = int(message.text.split("_")[-1])
    user = await get_or_create_user(message.from_user.id)
    task = await update_task_status(user["user_id"], cal_id, 1)
    if task:
        await message.answer(f"🔄 Задача <b>{task['text']}</b> отмечена как начато!")
    else:
        await message.answer("Задача не найдена")


@router.message(F.text.regexp(r"^/not_started_\d+$"))
async def cmd_skip(message: Message):
    cal_id = int(message.text.split("_")[-1])
    user = await get_or_create_user(message.from_user.id)
    task = await update_task_status(user["user_id"], cal_id, 0)
    if task:
        await message.answer(f"⬜ Задача <b>{task['text']}</b> возвращена в не начато!")
    else:
        await message.answer("Задача не найдена")


class DeleteCallback(CallbackData, prefix="del"):
    cal_id: int


@router.message(F.text.regexp(r"^/delete_\d+$"))
async def cmd_delete(message: Message):
    cal_id = int(message.text.split("_")[-1])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🗑 Да, удалить", callback_data=DeleteCallback(cal_id=cal_id).pack()),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    ]])
    await message.answer(f"Удалить задачу #{cal_id}?", reply_markup=keyboard)


@router.callback_query(DeleteCallback.filter())
async def confirm_delete(callback, callback_data: DeleteCallback):
    user = await get_or_create_user(callback.from_user.id)
    deleted = await delete_task(user["user_id"], callback_data.cal_id)
    if deleted:
        await callback.message.edit_text("🗑 Задача удалена!")
    else:
        await callback.message.edit_text("Задача не найдена")


@router.callback_query(F.data == "cancel")
async def cancel_delete(callback):
    await callback.message.edit_text("Отменено")