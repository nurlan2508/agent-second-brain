"""Process command handler."""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="process")
logger = logging.getLogger(__name__)


@router.message(Command("process"))
async def cmd_process(message: Message) -> None:
    """Handle /process command - deprecated on Linux VPS.
    
    NOTE: /process использовал Apple MCP (Reminders/Notes) которые не работают на Linux.
    Используйте вместо этого /do команду для обработки отдельных записей.
    """
    await message.answer(
        "⚠️ <b>/process недоступна на VPS</b>\n\n"
        "Apple Reminders/Notes MCP работают только на macOS.\n\n"
        "Вместо этого используйте:\n"
        "• <b>/do</b> — обработать отдельную запись через Claude\n"
        "• Отправьте голосовое или текстовое сообщение — автоматически сохранится в vault\n\n"
        "Ежедневная обработка запускается автоматически по расписанию на Mac."
    )
