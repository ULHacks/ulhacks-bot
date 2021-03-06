"""General bot stuff like on_ready"""

import traceback
import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.debug = False

    @commands.command(hidden=True)
    async def hi(self, ctx):
        await ctx.send("hi")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def debug(self, ctx, debug: bool):
        self.debug = debug
        await ctx.send(f"Debug set to {debug}")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}")
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="$help",
        )
        await self.bot.change_presence(activity=activity)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Print whole traceback if debugging
        if self.debug:
            traceback.print_exception(type(error), error, error.__traceback__)
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
        content = " ".join(parts)
        try:
            try:
                await ctx.send(content)
            except discord.Forbidden:
                await ctx.author.send(content)
        # Note down that something went wrong and ignore it
        except Exception as e:
            print(f"Error while sending error message: {e!r}")

def setup(bot):
    bot.add_cog(Info(bot))
