"""Provides a message command to forward a request to a specified channel"""

from discord.ext import commands

class Message(commands.Cog):
    def __init__(self, bot, *, message_channel_id):
        self.bot = bot
        self.message_channel_id = message_channel_id
        self.message_channel = None

    async def cog_before_invoke(self, ctx):
        # Ensures the message_channel exists
        if self.message_channel is None:
            self.message_channel = self.bot.get_channel(self.message_channel_id)
            if self.message_channel is None:
                raise RuntimeError("cannot get message channel")

    @commands.command()
    async def message(self, ctx, *, text=""):
        """Requests help from an organizer"""
        if not text:
            await ctx.send("Please add a message to your request")
            return
        parts = [ctx.author.mention, text]
        message_prefix = await self.bot.store.get("config:message:prefix")
        if message_prefix:
            parts.insert(0, f"{message_prefix}")
        await self.message_channel.send(" ".join(parts))
        await ctx.send(
            "Thanks for sending a message!"
            " An organizer will get back to you as soon as possible!"
        )

    @commands.command()
    @commands.is_owner()
    async def _set_message_prefix(self, ctx, *, prefix=""):
        """Updates or clears the message prefix"""
        if not prefix:
            await self.bot.store.set("config:message:prefix", "")
            await ctx.send("Cleared the message prefix")
        else:
            await self.bot.store.set("config:message:prefix", prefix)
            await ctx.send(f"Updated the message prefix to: {prefix}")

def setup(bot):
    bot.add_cog(Message(bot, message_channel_id=873653291614085180))
