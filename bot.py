import traceback
import sys
import asyncio
import discord
from discord.ext import commands
from config import DISCORD_TOKEN, GUILD_ID

print("=== Starting bot ===", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"discord.py version: {discord.__version__}", flush=True)


class VoiceTrackerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.voice_tracker")
        await self.load_extension("cogs.stats")

    async def on_ready(self):
        print(f"Logged in as {self.user}", flush=True)
        self.loop.create_task(self._sync_commands())

    async def _sync_commands(self):
        await self.wait_until_ready()
        try:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            commands_data = self.tree.get_commands(guild=guild)
            print(f"Syncing {len(commands_data)} commands to guild...", flush=True)
            synced = await asyncio.wait_for(self.tree.sync(guild=guild), timeout=15)
            print(f"Synced {len(synced)} slash commands", flush=True)
        except asyncio.TimeoutError:
            print("Sync timed out — commands may already be registered", flush=True)
        except Exception as e:
            print(f"Sync error: {type(e).__name__}: {e}", flush=True)


if __name__ == "__main__":
    try:
        bot = VoiceTrackerBot()
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"FATAL: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
