"""Button handlers for reply keyboard with GTD system."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from d_brain.bot.states import DoCommandState
from d_brain.bot.keyboards import get_main_keyboard

router = Router(name="buttons")


@router.message(F.text == "📥 Inbox")
async def btn_inbox(message: Message) -> None:
    """Handle Inbox button - show all inbox items."""
    await message.answer(
        "📥 <b>Inbox</b>\n\n"
        "Здесь хранятся все необработанные записи.\n\n"
        "Текущие записи:\n"
        "• Купить молоко завтра @дом\n\n"
        "Выбери запись для обработки или отправь новую.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "✅ Next Actions")
async def btn_next_actions(message: Message) -> None:
    """Handle Next Actions button - show actionable tasks."""
    await message.answer(
        "✅ <b>Next Actions</b>\n\n"
        "Твои текущие задачи, готовые к выполнению:\n"
        "• Купить молоко (завтра, @дом)\n"
        "• Отправить отчет (до пятницы, @работа)\n\n"
        "<i>Выполни одну из них и отправь /done</i>",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "⏳ Waiting")
async def btn_waiting(message: Message) -> None:
    """Handle Waiting For button - show waiting items."""
    await message.answer(
        "⏳ <b>Waiting For</b>\n\n"
        "Задачи, в которых ты ждешь ответа:\n"
        "• Ответ от Марата про проект\n"
        "• Доступ в систему от IT\n\n"
        "<i>Эти задачи не требуют твоего действия сейчас</i>",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "🎯 Goals")
async def btn_goals(message: Message) -> None:
    """Handle Goals button - show weekly goals."""
    await message.answer(
        "🎯 <b>Еженедельные Цели</b>\n\n"
        "<b>Неделя 8 (21-27 февраля 2026)</b>\n\n"
        "⚠️ <b>КРИТИЧНО:</b>\n"
        "• Оплатить кредит RBK (65,806.91 РУБ - просрочен на 3 дня!)\n"
        "• Оплатить Халык (275,000 РУБ - до 25 февраля)\n\n"
        "<b>Работа:</b>\n"
        "• Завершить отчет по проекту\n"
        "• Встреча с командой в среду\n\n"
        "<b>Личное:</b>\n"
        "• Записать видео для канала\n"
        "• Спортзал 3 раза",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "📅 Week Review")
async def btn_week_review(message: Message) -> None:
    """Handle Weekly Review button."""
    await message.answer(
        "📅 <b>Еженедельный обзор</b>\n\n"
        "Пожалуйста, выполните еженедельный GTD обзор:\n\n"
        "1️⃣ <b>Capture:</b> Просмотрите все записи\n"
        "2️⃣ <b>Clarify:</b> Определите следующие шаги\n"
        "3️⃣ <b>Organize:</b> Разместите в правильные списки\n"
        "4️⃣ <b>Reflect:</b> Оцените прогресс\n"
        "5️⃣ <b>Engage:</b> Выполните важные задачи\n\n"
        "Это займет около 30 минут.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "⚙️ Settings")
async def btn_settings(message: Message) -> None:
    """Handle Settings button."""
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Здесь можно настроить:\n"
        "• Время автоматической обработки (21:00)\n"
        "• Контексты по умолчанию\n"
        "• Уведомления\n"
        "• Синхронизацию с Google Services\n\n"
        "Скоро появится подробное меню!",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "❓ Help")
async def btn_help(message: Message) -> None:
    """Handle Help button."""
    from d_brain.bot.handlers.commands import cmd_help

    await cmd_help(message)
