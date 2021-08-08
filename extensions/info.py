"""General bot stuff like on_ready"""

import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hi(self, ctx):
        await ctx.send("hi")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}")
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="$help"
        )
        await self.bot.change_presence(activity=activity)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Unpack the error for cleaner error messages
        if isinstance(error, commands.CommandInvokeError):
            error = error.__cause__ or error
        try:
            await ctx.send(f"Oops, an error occurred: `{error!r}`")
        except Exception:
            print(f"Error: {error!r}")
            raise

def setup(bot):
    bot.add_cog(Info(bot))
