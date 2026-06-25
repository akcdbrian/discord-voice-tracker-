import discord
from discord import app_commands
from discord.ext import commands
from database import db


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="voicecount", description="Show how many times a user joined voice channels in the last 7 days"
    )
    async def voicecount(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()

        data = db.get_daily_join_counts(user.id, days=7)

        lines = [f"**{user.display_name}** — Voice Join Count (last 7 days)"]
        total = 0
        for row in data:
            lines.append(f"{row['date']}: {row['count']} time(s)")
            total += row["count"]
        lines.append(f"**Total: {total} time(s)**")

        await interaction.followup.send("\n".join(lines))

    @app_commands.command(
        name="voiceduration", description="Show total voice duration for a user in the last 7 days"
    )
    async def voiceduration(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()

        data = db.get_daily_durations(user.id, days=7)

        lines = [f"**{user.display_name}** — Voice Duration (last 7 days)"]
        total = 0
        for row in data:
            secs = row["total_seconds"]
            total += secs
            lines.append(f"{row['date']}: {self._format_duration(secs)}")
        lines.append(f"**Total: {self._format_duration(total)}**")

        await interaction.followup.send("\n".join(lines))

    @app_commands.command(
        name="check", description="Check if a user has been in voice channels each day for the last 7 days"
    )
    async def check(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()

        data = db.get_daily_join_counts(user.id, days=7)

        lines = [f"**{user.display_name}** — Voice Activity (last 7 days)"]
        for row in data:
            status = "Yes" if row["count"] > 0 else "No"
            lines.append(f"{row['date']}: {status}")

        await interaction.followup.send("\n".join(lines))

    @staticmethod
    def _format_duration(seconds: int) -> str:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
