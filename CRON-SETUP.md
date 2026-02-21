# Daily Processing Setup - Cron Configuration

## Problem Identified
User reported that system wasn't automatically processing entries at 21:00. Investigation revealed:
- ✗ No cron job configured for daily processing
- ✗ Python type hints incompatible with Python 3.9 on VPS
- ✗ Project dependencies not installed on VPS

## Solution Implemented

### 1. Fixed Python 3.9 Type Hint Incompatibilities

Modern Python union syntax (`str | Path`) requires Python 3.10+, but VPS runs Python 3.9.

**Files Fixed**:
- `src/d_brain/services/session.py`
  - Changed: `vault_path: Path | str`
  - To: `vault_path: Union[Path, str]`

- `src/d_brain/services/processor.py`
  - Changed: `day: date | None`
  - To: `day: Optional[date]`

### 2. Created Daily Processor Script

New file: `src/d_brain/scripts/daily_processor.py`

**What it does**:
1. Runs at 21:00 daily (VPS local time: Asia/Almaty +05)
2. Loads today's captured entries from session storage
3. Processes each entry with Claude API for classification
4. Creates tasks in Google Tasks with proper formatting
5. Logs all activities to `/tmp/d-brain-daily.log`

**Statistics collected**:
- Total entries processed
- Tasks created
- Notes created
- Waiting items
- Someday/Maybe items
- Processing errors

### 3. Installed Dependencies on VPS

Since VPS uses system Python 3.12.3, created virtual environment:

```bash
cd /home/ubuntu/projects/agent-second-brain
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 4. Configured Cron Job

Added to ubuntu user's crontab:

```bash
0 21 * * * cd /home/ubuntu/projects/agent-second-brain && source venv/bin/activate && python3 -m d_brain.scripts.daily_processor >> /tmp/d-brain-daily.log 2>&1
```

**Cron Details**:
- **Time**: 21:00 every day
- **Timezone**: Asia/Almaty (UTC+5)
- **Current local time on VPS**: 21:46 on 2026-02-21
- **Execution**: Activates venv, runs daily processor, logs output

## Verification

✅ **Cron job installed**:
```
0 21 * * 0 /home/ubuntu/n8n2/scripts/n8n_update.sh >> /home/ubuntu/n8n2/cron.log 2>&1
0 21 * * * cd /home/ubuntu/projects/agent-second-brain && source venv/bin/activate && python3 -m d_brain.scripts.daily_processor >> /tmp/d-brain-daily.log 2>&1
```

✅ **Daily processor tested on VPS**:
- Loads settings from `.env`
- Detects vault path
- Processes entries correctly
- Logs to `/tmp/d-brain-daily.log`

## System Flow

### Timeline

1. **24/7 (VPS Bot)**: Telegram messages captured
   - Saved to `vault/daily/{date}.txt`
   - Session stored in `.sessions/{user_id}.jsonl`
   - Response: "сохранено" (saved)

2. **21:00 Daily (VPS Cron)**: Processing phase
   - Cron triggers `daily_processor.py`
   - Loads today's entries from session
   - Claude API classifies each entry
   - Creates Google Tasks with proper dates
   - Logs results

3. **Google Tasks**: Tasks appear automatically
   - All tasks in "Second Brain" tasklist
   - Due dates properly formatted
   - Accessible from any device

## Timezone Information

**VPS Configuration**:
- Timezone: Asia/Almaty (UTC+5)
- Local time: 21:46 (when setup was completed)
- UTC time: 16:46

**Processing Time**: 21:00 daily (Almaty local time)

## Logs

Daily processor logs to:
- VPS: `/tmp/d-brain-daily.log`

Check logs:
```bash
ssh vps "tail -50 /tmp/d-brain-daily.log"
```

## What Happens on First Run

Since vault was recently deployed, first run will:
1. Load `.env` successfully
2. Check for entries (probably none if no messages captured yet)
3. Log "No entries captured today"
4. Exit cleanly

Once you start sending messages via bot, cron job will:
1. Load those messages
2. Classify them
3. Create Google Tasks
4. Log detailed results

## Testing

To manually test the daily processor:

```bash
ssh vps "cd /home/ubuntu/projects/agent-second-brain && source venv/bin/activate && python3 -m d_brain.scripts.daily_processor"
```

Or check if it ran automatically at 21:00:
```bash
ssh vps "tail -50 /tmp/d-brain-daily.log"
```

## Files Modified

1. `src/d_brain/scripts/daily_processor.py` - New script
2. `src/d_brain/scripts/__init__.py` - New init file
3. `src/d_brain/services/session.py` - Fixed type hints
4. `src/d_brain/services/processor.py` - Fixed type hints

## Next Steps

1. Send test messages via `/do` command
2. Check Google Tasks for created tasks at next 21:00 run
3. Verify logs in `/tmp/d-brain-daily.log`
4. System is ready for daily operations

## Troubleshooting

If cron doesn't run:

1. **Check cron installation**:
   ```bash
   ssh vps "crontab -l"
   ```

2. **Test processor manually**:
   ```bash
   ssh vps "cd /home/ubuntu/projects/agent-second-brain && source venv/bin/activate && python3 -m d_brain.scripts.daily_processor"
   ```

3. **Check logs**:
   ```bash
   ssh vps "tail -100 /tmp/d-brain-daily.log"
   ```

4. **Verify dependencies**:
   ```bash
   ssh vps "cd /home/ubuntu/projects/agent-second-brain && source venv/bin/activate && python3 -c 'import d_brain; print(\"OK\")'
   ```

