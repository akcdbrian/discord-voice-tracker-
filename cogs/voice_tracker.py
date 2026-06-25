import discord
from discord.ext import commands
from datetime import datetime, timezone
from database import db


class VoiceTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_sessions: dict[int, tuple[int, datetime]] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        db.init_db()
        self._close_dangling_sessions()
        self._track_current_vc_users()

    def _close_dangling_sessions(self):
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        open_sessions = db.get_open_sessions()
        for session in open_sessions:
            join_time = datetime.fromisoformat(session["join_time"])
            duration = int((now - join_time).total_seconds())
            db.close_session(session["id"], now_iso, duration)

    def _track_current_vc_users(self):
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        for vc in self.bot.get_all_channels():
            if isinstance(vc, discord.VoiceChannel):
                for member in vc.members:
                    if not member.bot and member.id not in self.active_sessions:
                        session_id = db.log_join(member.id, now_iso)
                        self.active_sessions[member.id] = (session_id, now)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member.bot:
            return

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        if before.channel is None and after.channel is not None:
            session_id = db.log_join(member.id, now_iso)
            self.active_sessions[member.id] = (session_id, now)

        elif before.channel is not None and after.channel is None:
            if member.id in self.active_sessions:
                session_id, join_time = self.active_sessions.pop(member.id)
                duration = int((now - join_time).total_seconds())
                db.log_leave(session_id, now_iso, duration)


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceTracker(bot))
