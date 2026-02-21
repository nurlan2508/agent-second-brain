"""Callback query handlers for inline buttons."""

import logging
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from d_brain.bot.keyboards import (
    get_task_type_keyboard,
    get_context_keyboard,
    get_priority_keyboard,
    get_confirm_keyboard,
    get_main_keyboard,
)

logger = logging.getLogger(__name__)

router = Router(name="callbacks")


# Task Type Callbacks
@router.callback_query(F.data.startswith("type_"))
async def handle_task_type(query: CallbackQuery, state: FSMContext) -> None:
    """Handle task type selection."""
    task_type = query.data.replace("type_", "")
    
    type_names = {
        "task": "📝 Задача",
        "project": "🚀 Проект",
        "reference": "📌 Справка",
        "waiting": "⏳ Ожидание",
        "someday": "📚 Когда-нибудь"
    }
    
    await state.update_data(task_type=task_type)
    
    await query.answer(f"✅ Выбран тип: {type_names.get(task_type)}")
    await query.message.edit_text(
        f"🎯 Тип: {type_names.get(task_type)}\n\n"
        f"Теперь выбери контекст (где выполнять?):",
        reply_markup=get_context_keyboard()
    )


# Context Callbacks
@router.callback_query(F.data.startswith("ctx_"))
async def handle_context(query: CallbackQuery, state: FSMContext) -> None:
    """Handle context selection."""
    context = query.data.replace("ctx_", "")
    
    context_names = {
        "work": "💼 @work",
        "home": "🏠 @home",
        "computer": "💻 @computer",
        "phone": "📱 @phone",
        "meetings": "👥 @meetings",
        "skip": "⏭️ Пропустить"
    }
    
    await state.update_data(context=context)
    await query.answer(f"✅ Контекст: {context_names.get(context)}")
    
    await query.message.edit_text(
        f"Контекст: {context_names.get(context)}\n\n"
        f"Выбери приоритет (важность):",
        reply_markup=get_priority_keyboard()
    )


# Priority Callbacks
@router.callback_query(F.data.startswith("priority_"))
async def handle_priority(query: CallbackQuery, state: FSMContext) -> None:
    """Handle priority selection."""
    priority = query.data.replace("priority_", "")
    
    priority_names = {
        "high": "🔴 Высокий",
        "normal": "🟡 Обычный",
        "low": "🟢 Низкий"
    }
    
    await state.update_data(priority=priority)
    await query.answer(f"✅ Приоритет: {priority_names.get(priority)}")
    
    # Get collected data
    data = await state.get_data()
    task_type = data.get('task_type', 'task')
    context = data.get('context', 'skip')
    priority = data.get('priority', 'normal')
    
    context_str = f"@{context}" if context != "skip" else "(без контекста)"
    
    await query.message.edit_text(
        f"📋 <b>Подтверди детали:</b>\n\n"
        f"Тип: 📝\n"
        f"Контекст: {context_str}\n"
        f"Приоритет: {priority_names.get(priority)}\n\n"
        f"Всё правильно?",
        reply_markup=get_confirm_keyboard()
    )


# Confirm Callbacks
@router.callback_query(F.data.startswith("confirm_"))
async def handle_confirm(query: CallbackQuery, state: FSMContext) -> None:
    """Handle confirmation."""
    action = query.data.replace("confirm_", "")
    
    if action == "yes":
        await query.answer("✅ Сохранено!")
        await query.message.edit_text(
            "✅ <b>Задача сохранена в Inbox</b>\n\n"
            "Она будет обработана автоматически в 21:00\n"
            "или выполните обработку вручную через /do",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
    else:
        await query.answer("❌ Отменено")
        await query.message.edit_text(
            "❌ Создание отменено",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
