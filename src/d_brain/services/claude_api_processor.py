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

        prompt = f"""Ты - GTD-ассистент. Твоя задача обработать эту запись используя Getting Things Done методологию.

Контекст:
- Дата: {today}
- Язык: русский

{session_context}

Запись для обработки:
"{text}"

ВЫПОЛНИ:
1. Проанализируй запись
2. Классифицируй по GTD категориям:
   - Задача (actionable item) - требует выполнения
   - Справка (reference) - информация для сохранения
   - Отложенное (waiting) - ожидание ответа от кого-то
   - Когда-нибудь (someday/maybe) - интересно но не срочно
3. Если это ЗАДАЧА:
   - Создай её в Google Tasks
   - Определи имеет ли она срок выполнения
4. Если это СПРАВКА:
   - Создай заметку в Google Keep
5. Верни результат в JSON:

{{
  "type": "task" | "note" | "waiting" | "someday",
  "title": "Заголовок",
  "content": "Полное содержание",
  "due_date": "YYYY-MM-DD" или null,
  "created": true/false,
  "status": "Статус выполнения"
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
                    task = self.tasks_service.create_task(
                        title=result["title"],
                        notes=result["content"],
                        due_date=result.get("due_date", ""),
                    )
                    result["created"] = True
                    result["status"] = "✓ Создана задача"
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
                    result["status"] = "✓ Создана заметка"
                    logger.info("Created note: %s", note.get("name"))
                except Exception as e:
                    logger.error("Failed to create note: %s", e)
                    result["created"] = False
                    result["status"] = f"Ошибка создания заметки: {e}"

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
