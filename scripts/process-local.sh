#!/bin/bash
set -e

# Local Mac processing script
# Pulls vault from VPS, runs Claude with Apple MCP, pushes back

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Paths
PROJECT_DIR="$HOME/Claude code/Second brain"
VAULT_DIR="$PROJECT_DIR/vault"
ENV_FILE="$PROJECT_DIR/.env"

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Check token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "ERROR: TELEGRAM_BOT_TOKEN not set"
    exit 1
fi

# MCP timeout
export MCP_TIMEOUT=30000
export MAX_MCP_OUTPUT_TOKENS=50000

# Date and chat_id
TODAY=$(date +%Y-%m-%d)
CHAT_ID="${ALLOWED_USER_IDS//[\[\]]/}"

echo "=== d-brain LOCAL processing for $TODAY ==="

# Pull latest vault from VPS
echo "=== Pulling vault from remote ==="
cd "$PROJECT_DIR"
git pull origin main || true

# Run Claude from vault/ with Apple MCP
cd "$VAULT_DIR"
REPORT=$(claude --print --dangerously-skip-permissions \
    --mcp-config "$PROJECT_DIR/mcp-config.json" \
    -p "Today is $TODAY. Execute daily processing according to dbrain-processor skill.

CRITICAL: MCP loads in 10-30 seconds. You are NOT in subprocess — MCP IS running, just initializing.

Algorithm:
1. Read daily/$TODAY.md entries
2. Read goals/3-weekly.md
3. For each entry, classify using GTD rules
4. Create tasks in Apple Reminders via mcp__apple-events
5. Save reference notes to Apple Notes via mcp__Read_and_Write_Apple_Notes
6. Generate HTML report

DO NOT say MCP unavailable. It is available. Just wait and call." \
    2>&1) || true
cd "$PROJECT_DIR"

echo "=== Claude output ==="
echo "$REPORT"
echo "===================="

# Remove HTML comments
REPORT_CLEAN=$(echo "$REPORT" | sed '/<!--/,/-->/d')

# Rebuild vault graph
echo "=== Rebuilding vault graph ==="
cd "$VAULT_DIR"
uv run .claude/skills/graph-builder/scripts/analyze.py || echo "Graph rebuild failed (non-critical)"
cd "$PROJECT_DIR"

# Git commit & push back
git add -A
git commit -m "chore: process daily $TODAY (local Mac)" || true
git push origin main || true

# Send to Telegram
if [ -n "$REPORT_CLEAN" ] && [ -n "$CHAT_ID" ]; then
    echo "=== Sending to Telegram ==="
    RESULT=$(curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$REPORT_CLEAN" \
        -d "parse_mode=HTML")

    if echo "$RESULT" | grep -q '"ok":false'; then
        echo "HTML failed: $RESULT"
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$CHAT_ID" \
            -d "text=$REPORT_CLEAN"
    fi
fi

echo "=== Done ==="
