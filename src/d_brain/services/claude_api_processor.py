"""Claude API processor for task/note extraction and creation."""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

import anthropic

from d_brain.services.google_keep import GoogleKeepService
from d_brain.services.google_tasks import GoogleTasksService
from d_brain.services.session import SessionStore

logger = logging.getLogger(__name__)


class ClaudeAPIProcessor:
    """Service for processing entries with Claude API and creating Google Tasks/Keep."""

    def __init__(self, vault_path: Path, google_credentials_path: str) -> None:
        """Initialize with vault path and Google credentials.

        Args:
            vault_path: Path to vault directory
            google_credentials_path: Path to Google Service Account credentials JSON
        """
        self.vault_path = Path(vault_path)
        self.client = anthropic.Anthropic()
        self.tasks_service = GoogleTasksService(google_credentials_path)
        self.keep_service = GoogleKeepService(google_credentials_path)

    def process_entry(self, text: str, user_id: int = 0) -> dict[str, Any]:
        """Process a single entry with Claude and create tasks/notes.

        Args:
            text: The entry text to process
            user_id: Telegram user ID for context

        Returns:
            Processing report as dict
        """
        today = date.today()

        # Get session context for GTD processing
        session_context = self._get_session_context(user_id)

        prompt = f"""Ты - GTD-ассистент. Твоя задача правильно обработать эту запись используя Getting Things Done методологию.

Контекст:
- Дата сегодня: {today}
- Язык: русский
- Вчерашние записи для контекста:

{session_context}

ЗАПИСЬ ДЛЯ ОБРАБОТКИ:
"{text}"

=== ИНСТРУКЦИИ ===

ПЕРВОЕ: Определи тип записи:

1. ЗАДАЧА (Task) - actionable item
   - Содержит глагол действия (купить, позвонить, написать, оплатить и т.д.)
   - Требует выполнения
   - Может быть простой (< 2 мин) или сложной (> 2 мин)
   - ПРИМЕРЫ: "Купить молоко", "Оплатить счет до пятницы", "Позвонить Ивану"

2. ПРОЕКТ (Project) - сложное действие с несколькими шагами
   - Содержит слово "Проект:" или описывает многошаговый процесс
   - ПРИМЕРЫ: "Проект: переделать дизайн сайта", "Написать отчёт с анализом данных"
   - ДЕЙСТВИЕ: всё равно создаёшь как task, но отмечаешь как project

3. СПРАВКА (Reference) - информация для сохранения, но не actionable
   - Нет глагола действия
   - Просто информация
   - ПРИМЕРЫ: "Контакт: Иван +7999123456", "Идея: новое название сайта"

4. ОЖИДАНИЕ (Waiting) - ждёшь ответа/информации от кого-то
   - Содержит "ждать ответ", "когда...", "как только..."
   - ПРИМЕРЫ: "Ждём ответ от Петра про встречу", "Как только получу доступ"

5. КОГДА-НИБУДЬ (Someday/Maybe) - интересно но не срочно
   - Содержит "может быть", "когда-нибудь", "в будущем"
   - ПРИМЕРЫ: "Когда-нибудь выучить японский", "Может быть, поехать в Японию"

ВТОРОЕ: Если это ЗАДАЧА или ПРОЕКТ:
- Определи срок выполнения:
  - "сегодня" → сегодняшняя дата
  - "завтра" → завтрашняя дата
  - "на этой неделе" → конец недели
  - "на следующей неделе" → следующий понедельник
  - "до ХХ числа" → то число
  - "не указан" → null
- Определи контекст (@work, @home, @phone, @computer)

ТРЕТЬЕ: Верни ТОЛЬКО JSON (БЕЗ других текстов):

{{
  "type": "task",
  "title": "короткий заголовок",
  "content": "полное описание задачи",
  "context": "@work или @home или @computer или @phone",
  "due_date": "YYYY-MM-DD или null",
  "priority": "high или medium или low",
  "is_project": false,
  "notes": "доп. заметки если нужны"
}}

ИЛИ для справки:

{{
  "type": "note",
  "title": "заголовок справки",
  "content": "содержание справки",
  "tags": ["метка1", "метка2"]
}}

ИЛИ для ожидания:

{{
  "type": "waiting",
  "title": "ждём ответ от кого",
  "content": "описание",
  "waiting_for": "имя человека или информация",
  "due_date": null
}}

ИЛИ для когда-нибудь:

{{
  "type": "someday",
  "title": "название идеи",
  "content": "описание",
  "tags": ["идея"]
}}"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            response_text = message.content[0].text

            # Try to extract JSON from response
            try:
                # Find JSON in response (it might be wrapped in text)
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    # Fallback: return as note
                    result = {
                        "type": "note",
                        "title": text[:50],
                        "content": text,
                        "created": False,
                        "status": "Не удалось распарсить ответ Claude",
                    }
            except json.JSONDecodeError:
                logger.warning("Failed to parse Claude response as JSON")
                result = {
                    "type": "note",
                    "title": text[:50],
                    "content": text,
                    "created": False,
                    "status": "Parsing error",
                }

            # Create task or note based on classification
            if result["type"] == "task":
                try:
                    # Determine which list to add to based on context/priority
                    list_name = "Next Actions"
                    if result.get("priority") == "high" or result.get("context") == "@phone":
                        list_name = "Next Actions"
                    elif result.get("is_project"):
                        list_name = "Projects"
                    
                    task = self.tasks_service.create_task(
                        title=result["title"],
                        notes=result["content"],
                        due_date=result.get("due_date", ""),
                    )
                    result["created"] = True
                    result["status"] = f"✓ Создана задача в {list_name}"
                    logger.info("Created task: %s", task.get("id"))
                except Exception as e:
                    logger.error("Failed to create task: %s", e)
                    result["created"] = False
                    result["status"] = f"Ошибка создания задачи: {e}"

            elif result["type"] == "note":
                try:
                    note = self.keep_service.create_note(
                        title=result["title"],
                        content=result["content"],
                    )
                    result["created"] = True
                    result["status"] = "✓ Создана заметка в Google Keep"
                    logger.info("Created note: %s", note.get("name"))
                except Exception as e:
                    logger.error("Failed to create note: %s", e)
                    result["created"] = False
                    result["status"] = f"Ошибка создания заметки: {e}"

            elif result["type"] == "waiting":
                try:
                    # Create as task with note that we're waiting
                    waiting_note = f"⏳ Ожидаем: {result.get('waiting_for', 'ответ')}\n\n{result.get('content', '')}"
                    task = self.tasks_service.create_task(
                        title=f"⏳ {result['title']}",
                        notes=waiting_note,
                        due_date=result.get("due_date", ""),
                    )
                    result["created"] = True
                    result["status"] = "✓ Добавлено в Waiting For"
                    logger.info("Created waiting task: %s", task.get("id"))
                except Exception as e:
                    logger.error("Failed to create waiting task: %s", e)
                    result["created"] = False
                    result["status"] = f"Ошибка: {e}"

            elif result["type"] == "someday":
                try:
                    # Create as note in Google Keep with someday tag
                    note = self.keep_service.create_note(
                        title=f"📚 {result['title']}",
                        content=result["content"],
                    )
                    result["created"] = True
                    result["status"] = "✓ Добавлено в Someday/Maybe"
                    logger.info("Created someday note: %s", note.get("name"))
                except Exception as e:
                    logger.error("Failed to create someday note: %s", e)
                    result["created"] = False
                    result["status"] = f"Ошибка: {e}"

            return result

        except anthropic.APIError as e:
            logger.error("Claude API error: %s", e)
            return {
                "type": "error",
                "status": f"API error: {e}",
                "created": False,
            }
        except Exception as e:
            logger.exception("Unexpected error during processing")
            return {
                "type": "error",
                "status": f"Error: {e}",
                "created": False,
            }

    def _get_session_context(self, user_id: int) -> str:
        """Get today's session context for Claude.

        Args:
            user_id: Telegram user ID

        Returns:
            Recent session entries formatted for inclusion in prompt.
        """
        if user_id == 0:
            return ""

        try:
            session = SessionStore(self.vault_path)
            today_entries = session.get_today(user_id)
            if not today_entries:
                return ""

            lines = ["=== КОНТЕКСТ СЕГОДНЯ ==="]
            for entry in today_entries[-5:]:
                ts = entry.get("ts", "")[11:16]  # HH:MM from ISO
                entry_type = entry.get("type", "unknown")
                text = entry.get("text", "")[:60]
                if text:
                    lines.append(f"{ts} [{entry_type}] {text}...")
            lines.append("=== КОНЕЦ КОНТЕКСТА ===\n")
            return "\n".join(lines)
        except Exception as e:
            logger.warning("Failed to get session context: %s", e)
            return ""
