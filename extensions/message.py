"""Provides a message command to forward a request to a specified channel"""

from discord.ext import commands

class Message(commands.Cog):
    TYPES = tuple("message register hacker".split())

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
        """Send a message to the organizers who will get back to you ASAP"""
        if not text:
            await ctx.send("Please add a message to your request")
            return
        parts = [ctx.author.mention, text]
        message_prefix = await self.bot.store.get("message:prefix:message")
        if message_prefix:
            parts.insert(0, f"{message_prefix}")
        await self.message_channel.send(" ".join(parts))
        await ctx.send(
            "Thanks for sending a message!"
            " An organizer will get back to you as soon as possible!"
        )

    @commands.command()
    async def register(self, ctx, *, text=""):
        """Send a message to the organizers to notify them of your role"""
        if not text:
            await ctx.send("Please add a message to your request")
            return
        parts = [ctx.author.mention, text]
        message_prefix = await self.bot.store.get("message:prefix:register")
        if message_prefix:
            parts.insert(0, message_prefix)
        await self.message_channel.send(" ".join(parts))
        await ctx.send(
            "Thanks for sending a message!"
            " An organizer will set you up as soon as possible!"
        )

    @commands.command()
    async def hacker(self, ctx):
        """Notify the organizers of your participation"""
        parts = [ctx.author.mention]
        message_prefix = await self.bot.store.get("message:prefix:hacker")
        if message_prefix:
            parts.insert(0, message_prefix)
        await self.message_channel.send(" ".join(parts))
        await ctx.send(
            "Thanks for participating in ULHacks!"
            " An organizer will verify you as soon as possible!"
        )

    @commands.command()
    @commands.is_owner()
    async def _set_prefix(self, ctx, type_, *, prefix=None):
        """Updates or clears the prefix for the specified type"""
        if type_ not in self.TYPES:
            await ctx.send(f"Type not one of {', '.join(self.TYPES)}")
            return
        if prefix is None:
            # Get prefix
            prefix = await self.bot.store.get(f"message:prefix:{type_}")
            await ctx.send(f"The {type_} prefix is: {prefix}")
        elif prefix == '""':
            # Clear prefix
            await self.bot.store.set(f"message:prefix:{type_}", "")
            await ctx.send(f"Cleared the {type_} prefix")
        else:
            # Update prefix
            await self.bot.store.set(f"message:prefix:{type_}", prefix)
            await ctx.send(f"Updated the {type_} prefix to: {prefix}")

def setup(bot):
    bot.add_cog(Message(bot, message_channel_id=873653291614085180))
