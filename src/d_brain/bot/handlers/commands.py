"""Command handlers for /start, /help, /status."""

from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from d_brain.bot.keyboards import get_main_keyboard
from d_brain.config import get_settings
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="commands")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "<b>🧠 d-brain GTD System</b> - твой персональный помощник\n\n"
        "<b>Как это работает:</b>\n\n"
        "1️⃣ <b>Capture:</b> Отправляй мне голосовые, текст, фото\n"
        "🎤 Голосовые — автоматически транскрибирую\n"
        "💬 Текст — сохраню как есть\n"
        "📷 Фото — архивирую\n\n"
        "2️⃣ <b>Organize:</b> Используй кнопки ниже для навигации\n"
        "📥 Inbox — необработанные записи\n"
        "✅ Next Actions — твои задачи\n"
        "⏳ Waiting — что ты ожидаешь\n"
        "🎯 Goals — еженедельные цели\n\n"
        "3️⃣ <b>Process:</b> Вечером в 21:00 автоматически обрабатываю",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    await message.answer(
        "<b>📖 Справка по GTD системе</b>\n\n"
        "<b>Основной workflow:</b>\n"
        "1. Отправляй голосовое или текст → я сохраняю в Inbox\n"
        "2. Вечером система обрабатывает записи\n"
        "3. Задачи переходят в 'Next Actions'\n"
        "4. Выполняй по одной из списка\n"
        "5. Еженедельный обзор (понедельник)\n\n"
        "<b>Типы записей:</b>\n"
        "📝 <b>Task</b> — задача с действием\n"
        "🚀 <b>Project</b> — многошаговый проект\n"
        "📌 <b>Reference</b> — информация/идея\n"
        "⏳ <b>Waiting</b> — жду ответ/помощь\n"
        "📚 <b>Someday</b> — интересно но не срочно\n\n"
        "<b>Контексты:</b>\n"
        "💼 @work — на работе\n"
        "🏠 @home — дома\n"
        "💻 @computer — за компьютером\n"
        "📱 @phone — с телефоном\n"
        "👥 @meetings — встречи\n\n"
        "<b>Команды:</b>\n"
        "/status — сколько записей\n"
        "/do — обработать одну запись\n"
        "/weekly — недельный обзор\n\n"
        "👇 Используй кнопки ниже для быстрого доступа",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    """Handle /status command."""
    user_id = message.from_user.id if message.from_user else 0
    settings = get_settings()
    storage = VaultStorage(settings.vault_path)

    # Log command
    session = SessionStore(settings.vault_path)
    session.append(user_id, "command", cmd="/status")

    today = date.today()
    content = storage.read_daily(today)

    if not content:
        await message.answer(
            f"📅 <b>{today}</b>\n\nЗаписей пока нет.",
            reply_markup=get_main_keyboard()
        )
        return

    lines = content.strip().split("\n")
    entries = [line for line in lines if line.startswith("## ")]

    voice_count = sum(1 for e in entries if "[voice]" in e)
    text_count = sum(1 for e in entries if "[text]" in e)
    photo_count = sum(1 for e in entries if "[photo]" in e)
    forward_count = sum(1 for e in entries if "[forward from:" in e)

    total = len(entries)

    # Get weekly stats from session
    week_stats = ""
    stats = session.get_stats(user_id, days=7)
    if stats:
        week_stats = "\n\n<b>За 7 дней:</b>"
        for entry_type, count in sorted(stats.items()):
            week_stats += f"\n• {entry_type}: {count}"

    await message.answer(
        f"📅 <b>{today}</b>\n\n"
        f"Всего записей: <b>{total}</b>\n"
        f"- 🎤 Голосовых: {voice_count}\n"
        f"- 💬 Текстовых: {text_count}\n"
        f"- 📷 Фото: {photo_count}\n"
        f"- ↩️ Пересланных: {forward_count}"
        f"{week_stats}",
        reply_markup=get_main_keyboard()
    )
