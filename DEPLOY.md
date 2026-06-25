# Deploy to Railway

## 1. Create a Discord Bot

1. Go to https://discord.com/developers/applications → New Application → name it
2. Go to **Bot** tab → Reset Token → copy the token (save it somewhere safe)
3. Under **Privileged Gateway Intents**, enable:
   - **Server Members Intent**
   - **Message Content Intent**
   - **Voice State Intent**
4. Go to **OAuth2** → **URL Generator**
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `View Channels`, `Connect`, `Speak`, `Use Slash Commands`
   - Copy the generated URL and open it in a browser to invite the bot to your server

## 2. Get Your Guild ID

1. In Discord, go to User Settings → **Advanced** → enable **Developer Mode**
2. Right-click your server name → **Copy ID**
3. Save this — it's your `GUILD_ID`

## 3. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Discord voice tracker bot"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## 4. Deploy on Railway

1. Go to https://railway.app → Sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo** → select your repo
3. Railway auto-detects `requirements.txt` and `Procfile`
4. Go to **Variables** and add:
   - `DISCORD_TOKEN` = your bot token
   - `GUILD_ID` = your server ID
5. Railway will build and deploy automatically
6. Your bot is now running 24/7

## 5. Verify

- Open Discord and type `/voicecount @yourself` — the slash commands should appear
- Join a voice channel, leave, then run `/voicecount @yourself` to confirm tracking works
