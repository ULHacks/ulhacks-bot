"""Binds a listener for members joining the ULHacks server"""

import asyncio
from discord.ext import commands

class Welcome(commands.Cog):
    DEFAULT_WELCOME_FILENAME = "welcome-message.md"
    def __init__(self, bot, *, guild_id, welcome_filename=None):
        if welcome_filename is None:
            welcome_filename = type(self).DEFAULT_WELCOME_FILENAME
        self.bot = bot
        self.guild_id = guild_id
        self.welcome_filename = welcome_filename

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != self.guild_id:
            return
        content = await asyncio.to_thread(self._get_welcome_message)
        await member.send(content)

    def _get_welcome_message(self):
        with open(self.welcome_filename) as file:
            return file.read()

def setup(bot):
    bot.add_cog(Welcome(bot, guild_id=871391148239880252))
