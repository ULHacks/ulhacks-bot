"""General bot stuff like on_ready"""

import traceback
import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
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
        parts = []
        # Get the original error causing this
        original = getattr(error, "original", None)
        if original is not None:
            wrapper, error = error, original
            parts += ["wrapped by", f"`{type(wrapper).__name__}`"]
        # Get the list of errors causing this
        errors = getattr(error, "errors", None)
        if errors is not None:
            parts += ["with errors:"]
            for cause_error in errors:
                parts += [f"`{cause_error!r}`"]
                parts += ["and"]
            parts.pop()
        # Add the base error
        parts[:0] = ["Oops, an error occurred:", f"`{error!r}`"]
        # Send the error message
        try:
            await ctx.send(" ".join(parts))
        # Note down that something went wrong and ignore it
        except Exception as e:
            print(f"Error while sending error message: {e!r}")

def setup(bot):
    bot.add_cog(Info(bot))
