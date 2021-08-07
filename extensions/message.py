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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def message(self, ctx, *, text=""):
        """Send a message to the organizers who will get back to you ASAP"""
        if not text:
            await ctx.send("Please add a message to your request")
            return
        parts = [f"{ctx.author.mention}:", text]
        prefix = await self.bot.store.get("message:prefix:message")
        if prefix:
            parts.insert(0, prefix)
        await self.message_channel.send(" ".join(parts))
        await ctx.send(
            "Thanks for sending a message!"
            " An organizer will get back to you as soon as possible!"
        )

    @commands.command()
    async def register(self, ctx, *, text=""):
        """Send a message to the organizers to notify them of your role"""
        if await self.bot.store.get(f"message:register:{ctx.author.id}"):
            await ctx.send(
                "You already registered. If you have any questions, please use"
                " the `$message` command to contact an organizer. (Example:"
                " `$message I don't think I registered yet`)"
            )
            return
        if not text:
            await ctx.send("Please add a message to your request")
            return
        parts = [f"{ctx.author.mention}:", text]
        prefix = await self.bot.store.get("message:prefix:register")
        if prefix:
            parts.insert(0, prefix)
        await self.message_channel.send(" ".join(parts))
        await self.bot.store.set(f"message:register:{ctx.author.id}", "1")
        await ctx.send(
            "Thanks for helping out with ULHacks!"
            " An organizer will set you up as soon as possible!"
        )

    @commands.command()
    async def hacker(self, ctx):
        """Notify the organizers of your participation"""
        if await self.bot.store.get(f"message:hacker:{ctx.author.id}"):
            await ctx.send(
                "You have already sent a verification request with `$hacker`."
                " If you have any questions, please use the `$message` command"
                " to contact an organizer. (Example: `$message it's been 3"
                " days since my $hacker request, could you make sure it went"
                " through?`)"
            )
            return
        parts = [f"{ctx.author.mention}:"]
        prefix = await self.bot.store.get("message:prefix:hacker")
        if prefix:
            parts.insert(0, prefix)
        await self.message_channel.send(" ".join(parts))
        await self.bot.store.set(f"message:hacker:{ctx.author.id}", "1")
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
