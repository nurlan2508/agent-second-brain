# Apple Reminders Integration

<!--
╔══════════════════════════════════════════════════════════════════╗
║  КАК НАСТРОИТЬ ЭТОТ ФАЙЛ                                         ║
╠══════════════════════════════════════════════════════════════════╣
║  1. Замените [Your List Names] на имена твоих списков Reminders  ║
║  2. Укажи свой основной список для задач                         ║
║  3. Измените примеры задач на релевантные для тебя               ║
║  4. Удали этот комментарий после настройки                       ║
╚══════════════════════════════════════════════════════════════════╝
-->

## Available MCP Tools

### Reading Reminders
- `get_lists` — все списки в Apple Reminders
- `get_reminders` — задачи из конкретного списка
- `search_reminders` — поиск по тексту

### Writing Reminders
- `create_reminder` — создать новое напоминание
- `complete_reminder` — отметить как выполненное
- `delete_reminder` — удалить напоминание

---

## My Reminder Lists

<!--
Укажи свои списки в Apple Reminders. Примеры:
-->

| List Name | Назначение |
|-----------|-----------|
| Входящие (Reminders) | Быстрые задачи без категории |
| Работа | Рабочие задачи |
| Личное | Личные дела |
| Покупки | Список покупок |

Default list for new tasks: **Входящие** (or first available list)

---

## Pre-Creation Checklist

### 1. Get lists (REQUIRED first step)

```
get_lists → choose appropriate list for the task
```

### 2. Check for duplicates

```
get_reminders → list name → search for similar tasks
```

If similar exists → skip creation, mention in report.

---

## Priority Mapping

Apple Reminders priorities: **none**, **low**, **medium**, **high**

| Context | Priority |
|---------|----------|
| Клиентский дедлайн, срочно | high |
| Важно, ONE Big Thing | medium |
| Обычные задачи | low |
| Стратегические, R&D | none |

---

## Date Mapping

| Context | Due Date |
|---------|----------|
| Клиентский дедлайн | точная дата |
| Срочное | сегодня / завтра |
| На этой неделе | пятница |
| На следующей неделе | следующий понедельник |
| Не указано | через 3 дня |

### Русский → due date

| Русский | Значение |
|---------|---------|
| сегодня | today |
| завтра | tomorrow |
| послезавтра | in 2 days |
| в понедельник | next monday |
| в пятницу | friday |
| на этой неделе | friday |
| на следующей неделе | next monday |
| через неделю | in 7 days |
| 15 января | January 15 |

---

## Reminder Creation

```
create_reminder:
  title: "Название задачи"
  list: "Название списка"
  due_date: "2025-02-20T10:00:00"  # ISO format, optional
  notes: "Дополнительные детали"   # optional
  priority: "medium"               # none/low/medium/high
```

### Title Style

User prefers: прямота, ясность, конкретика

✅ Good:
- "Отправить презентацию клиенту"
- "Позвонить врачу"
- "Оплатить счёт до пятницы"

❌ Bad:
- "Подумать о презентации"
- "Что-то с клиентом"
- "Разобраться с задачей"

---

## Anti-Patterns (НЕ СОЗДАВАТЬ)

- ❌ "Подумать о..." → конкретизируй действие
- ❌ "Разобраться с..." → что именно сделать?
- ❌ Абстрактные задачи без Next Action
- ❌ Дубликаты существующих задач

---

## Error Handling

CRITICAL: Никогда не предлагай "добавь вручную".

If `create_reminder` fails:
1. Include EXACT error message in report
2. Continue with next entry
3. Don't mark as processed

WRONG output:
  "Не удалось добавить (MCP недоступен). Добавь вручную: Task title"

CORRECT output:
  "Ошибка создания напоминания: [exact error from MCP tool]"
