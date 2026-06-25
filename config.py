import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not set in .env file")
if not GUILD_ID:
    raise ValueError("GUILD_ID not set in .env file")
