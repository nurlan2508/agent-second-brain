"""Weekly digest command handler."""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="weekly")
logger = logging.getLogger(__name__)


@router.message(Command("weekly"))
async def cmd_weekly(message: Message) -> None:
    """Handle /weekly command - deprecated on Linux VPS.
    
    NOTE: /weekly использовал Apple MCP (Reminders/Notes) которые не работают на Linux.
    """
    await message.answer(
        "⚠️ <b>/weekly недоступна на VPS</b>\n\n"
        "Apple Reminders/Notes MCP работают только на macOS.\n\n"
        "GTD Weekly Review запускается автоматически на Mac по расписанию "
        "(обычно в выходной день).\n\n"
        "Для ручного запуска используйте Mac версию через Claude Code."
    )
