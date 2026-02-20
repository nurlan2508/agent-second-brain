# Agent Second Brain

Voice-first personal assistant for capturing thoughts and managing tasks via Telegram. GTD methodology. Apple ecosystem (Reminders + Notes).

## EVERY SESSION BOOTSTRAP

**Before doing anything else, read these files in order:**

1. `vault/MEMORY.md` — curated long-term memory (preferences, decisions, context)
2. `vault/daily/YYYY-MM-DD.md` — today's entries
3. `vault/daily/YYYY-MM-DD.md` — yesterday's entries (for continuity)
4. `vault/goals/3-weekly.md` — this week's ONE Big Thing

**Don't ask permission, just do it.** This ensures context continuity across sessions.

---

## SESSION END PROTOCOL

**Before ending a significant session, write to today's daily:**

```markdown
## HH:MM [text]
Session summary: [what was discussed/decided/created]
- Key decision: [if any]
- Created: [if any tasks/notes created]
- Next action: [if any]
```

**Also update `vault/MEMORY.md` if:**
- New key decision was made
- User preference discovered
- Important fact learned
- Active context changed significantly

---

## Mission

Help user stay aligned with goals, capture valuable insights, and maintain clarity using GTD methodology.

## Directory Structure

| Folder | Purpose |
|--------|---------|
| `daily/` | Raw daily entries (YYYY-MM-DD.md) |
| `goals/` | Goal cascade (3y → yearly → monthly → weekly) |
| `thoughts/` | Processed notes by category |
| `MOC/` | Maps of Content indexes |
| `attachments/` | Photos by date |
| `gtd-capture/` | GTD dump files (reminders-dump.md, notes-dump.md) |

## Entry Format

```markdown
## HH:MM [type]
Content
```

Types: `[voice]`, `[text]`, `[forward from: Name]`, `[photo]`

## Processing Workflow

Run daily processing via `/process` command or automatically at 21:00.

### GTD Process Flow:
1. Read goals/ → understand priorities
2. Verify Apple MCP → check Reminders lists
3. Read daily/ → classify entries using GTD decision tree
4. Actionable? → route to Apple Reminders (right list)
5. Reference? → save to Apple Notes (right folder)
6. Generate HTML report → send to Telegram

## Available Skills

| Skill | Purpose |
|-------|---------|
| `dbrain-processor` | Main daily GTD processing |
| `graph-builder` | Vault link analysis and building |

## Available Agents

| Agent | Purpose |
|-------|---------|
| `weekly-digest` | GTD Weekly Review |
| `inbox-processor` | GTD inbox processing |

## MCP Servers

- `apple-events` — Apple Reminders + Calendar (tasks, events)
- `apple-notes` — Apple Notes (reference material, project descriptions)

## CRITICAL: Tool Usage Policy

**ТЫ ОБЯЗАН ВЫЗЫВАТЬ MCP TOOLS НАПРЯМУЮ.**

Не существует ситуации, когда MCP tools "недоступны". Если ты получил эту инструкцию — у тебя есть доступ к:

- `mcp__apple-events__*` — Apple Reminders и Calendar операции
- `mcp__Read_and_Write_Apple_Notes__*` — Apple Notes операции
- File read/write — все файловые операции

ЗАПРЕЩЁННЫЕ ПАТТЕРНЫ (НИКОГДА не делай это):
- "MCP недоступен в текущем режиме"
- "Не удалось добавить автоматически"
- "Добавь вручную: ..."
- Любые инструкции для ручного выполнения

ПРАВИЛЬНЫЙ ПАТТЕРН:
1. Вызвать mcp__apple-events__reminders_tasks action:create
2. Получить результат (успех или ошибка)
3. Включить результат в HTML отчёт

При ошибке — показать ТОЧНУЮ ошибку от tool, не придумывать отговорки.

## MCP Tools Available

**Apple Events (mcp__apple-events__*):**
- `reminders_tasks` action:read — читать напоминания (filterList, search, dueWithin)
- `reminders_tasks` action:create — создать напоминание (title, targetList, dueDate, note)
- `reminders_tasks` action:update — обновить напоминание (id, title, completed, targetList)
- `reminders_tasks` action:delete — удалить напоминание (id)
- `reminders_lists` action:read — все списки
- `calendar_events` action:create — создать событие (title, startDate, endDate)
- `calendar_events` action:read — читать события

**Apple Notes (mcp__Read_and_Write_Apple_Notes__*):**
- `list_notes` — список заметок в папке (folder, limit)
- `get_note_content` — содержимое заметки (note_name, folder)
- `add_note` — создать заметку (name, content, folder)
- `update_note_content` — обновить заметку (note_name, new_content, folder)

**Filesystem:**
- Read/write vault files
- Access daily/, goals/, thoughts/

## Apple Reminders Lists (GTD)

| GTD Зона | Список |
|----------|--------|
| 📥 Inbox | inbox |
| ⚡ Next Actions | Срочные |
| ⏳ Waiting For | Отложенные |
| 🌙 Someday/Maybe | Когда-нибудь/ может быть |
| 🏥 Health | Здоровье |
| 👨‍👩‍👧‍👦 Family | Family |
| 💰 Finance | Кредиты |
| 🤖 AI Projects | монетизация AI |
| 🏛️ Fund | Фонд |
| 🎯 Personal | Личные проекты |
| 📚 Learning | Обучение |

## Report Format

Reports use Telegram HTML:
- `<b>bold</b>` for headers
- `<i>italic</i>` for metadata
- Only allowed tags: b, i, code, s, u, a

## Quick Commands

| Command | Action |
|---------|--------|
| `/process` | Run daily GTD processing |
| `/do` | Execute arbitrary request |
| `/weekly` | Generate GTD weekly review |
| `/graph` | Analyze vault links |

## /do Command Context

When invoked via /do, Claude receives arbitrary user requests. Common patterns:

**Task Management (Apple Reminders):**
- "покажи задачи на сегодня"
- "добавь задачу: позвонить клиенту"
- "что срочного на этой неделе?"
- "перенеси задачу X на понедельник"

**Notes (Apple Notes):**
- "найди заметки про AI"
- "создай заметку о проекте БигШанхай"

**Vault Queries:**
- "что я записал сегодня?"
- "покажи итоги недели"

## Learnings (from experience)

1. **Don't rewrite working code** without reason (KISS, DRY, YAGNI)
2. **Don't add checks** that weren't there — let the agent decide
3. **Don't propose solutions** without studying git log/diff first
4. **Don't break architecture** (process.sh → Claude → skill is correct)
5. **Problems are usually simple** (e.g., sed one-liner for HTML fix)

---

*System Version: 3.0*
*Updated: 2026-02-20*
*Stack: Apple Reminders + Apple Notes (no Todoist, no Obsidian)*
