"""Reply keyboards for Telegram bot with GTD system."""

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Main GTD keyboard with quick access to key lists."""
    builder = ReplyKeyboardBuilder()
    
    # Row 1: Primary GTD workflow
    builder.button(text="📥 Inbox")
    builder.button(text="✅ Next Actions")
    builder.button(text="⏳ Waiting")
    
    # Row 2: Planning and goals
    builder.button(text="🎯 Goals")
    builder.button(text="📅 Week Review")
    
    # Row 3: System
    builder.button(text="⚙️ Settings")
    builder.button(text="❓ Help")
    
    builder.adjust(3, 2, 2)  # 3, 2, 2 buttons per row
    return builder.as_markup(resize_keyboard=True, is_persistent=True)


def get_task_type_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for choosing task type."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📝 Task", callback_data="type_task")
    builder.button(text="🚀 Project", callback_data="type_project")
    builder.button(text="📌 Reference", callback_data="type_reference")
    builder.button(text="⏳ Waiting For", callback_data="type_waiting")
    builder.button(text="📚 Someday", callback_data="type_someday")
    
    builder.adjust(2, 2, 1)  # 2, 2, 1 buttons per row
    return builder.as_markup()


def get_context_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for choosing context."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="💼 @work", callback_data="ctx_work")
    builder.button(text="🏠 @home", callback_data="ctx_home")
    builder.button(text="💻 @computer", callback_data="ctx_computer")
    builder.button(text="📱 @phone", callback_data="ctx_phone")
    builder.button(text="👥 @meetings", callback_data="ctx_meetings")
    builder.button(text="⏭️ Skip", callback_data="ctx_skip")
    
    builder.adjust(2, 2, 2)  # 2, 2, 2 buttons per row
    return builder.as_markup()


def get_priority_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for choosing priority."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🔴 High", callback_data="priority_high")
    builder.button(text="🟡 Normal", callback_data="priority_normal")
    builder.button(text="🟢 Low", callback_data="priority_low")
    
    builder.adjust(3)
    return builder.as_markup()


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for confirming action."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Confirm", callback_data="confirm_yes")
    builder.button(text="❌ Cancel", callback_data="confirm_no")
    
    builder.adjust(2)
    return builder.as_markup()
