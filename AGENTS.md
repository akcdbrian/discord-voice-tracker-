# AGENTS.md

Discord voice activity tracker bot. Python + discord.py + SQLite. Deployed on Railway.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in DISCORD_TOKEN and GUILD_ID
python bot.py
```

## Config

- `DISCORD_TOKEN` — bot token from Discord Developer Portal
- `GUILD_ID` — your Discord server ID (right-click server name → Copy ID)

Both required in `.env`. Never hardcode the token.

## Architecture

```
bot.py              → entrypoint, creates bot, loads cogs, syncs slash commands to guild
config.py           → reads .env via python-dotenv
database/db.py      → SQLite layer (voice_sessions table: user_id, join_time, leave_time, duration_seconds, date)
cogs/voice_tracker.py  → on_voice_state_update listener, tracks active sessions in memory
cogs/stats.py        → slash commands: /voicecount, /voiceduration, /check
```

## Discord setup

- **Intents required** (both in code AND Discord Dev Portal):
  - `voice_states` — to detect voice joins/leaves
  - `message_content` — required for command context
- **Bot invite URL**: must include `bot` + `applications.commands` scopes
- **Slash commands sync to guild only** (not global) → instant registration, no 1-hour delay
- **Critical**: must call `bot.tree.copy_global_to(guild=...)` before `bot.tree.sync(guild=...)`. Without it, syncing to a guild deletes all commands because commands defined via `@app_commands.command` in cogs are global by default, not guild-specific. Syncing guild-specific commands when none exist overwrites the global commands with an empty list.

## Key implementation details

- Voice sessions are tracked with an in-memory `dict[user_id → (session_db_id, join_timestamp)]`
- On bot restart, all open sessions are closed with the current time as leave_time
- Channel moves (A→B) do NOT count as a new join; only going from no-VC to VC creates a new session
- All 3 slash commands always show the full last 7 days (days with zero activity show `0` or `No`)
- SQLite file (`voice_data.db`) is created in the bot root directory at first startup

## Commands

```
/voicecount @user    — per-day join counts, last 7 days + total
/voiceduration @user — per-day total voice time, last 7 days + total
/check @user         — per-day yes/no voice activity, last 7 days
```

## Deployment (Railway)

- `Procfile` uses `worker:` (not `web:`) since this is a persistent process, not an HTTP server
- Set `DISCORD_TOKEN` and `GUILD_ID` as Railway environment variables (not via .env file on the server)
- Railway auto-installs from `requirements.txt`
- `.env` and `*.db` are in `.gitignore` — never committed

## Testing locally

No test framework configured. Manual testing:
1. Set up `.env` with a test bot token and test guild ID
2. Run `python bot.py`
3. Join/leave voice channels and run slash commands to verify tracking
