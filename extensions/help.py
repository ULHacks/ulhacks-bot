"""Handles help categories and channels"""

import traceback
import discord
from discord.ext import commands

async def is_help_channel_check(ctx):
    """Returns True when in a help channel"""
    if await ctx.cog.is_help_channel(ctx.channel):
        return True
    else:
        raise commands.CheckFailure("Current channel ain't a help channel")

async def is_help_channel_owner_check(ctx):
    """Returns True if invoker is the channel creator"""
    try:
        owner_id = await ctx.cog.get_channel_owner(ctx.channel)
    except LookupError:
        return False
    if owner_id == ctx.author.id:
        return True
    else:
        raise commands.CheckFailure("You aren't the help channel creator")

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check_any(
        commands.has_permissions(manage_guild=True),
        commands.has_role("Organizer"),
    )
    async def helpcategory(self, ctx, *, name=None):
        """Gets or sets the name of this server's help category"""
        if name is None:
            name = await self.get_category_name(ctx.guild)
            await ctx.send(f"This server's help category name is: {name}")
        else:
            if name == '""':
                name = ""
            await self.set_category_name(ctx.guild, name)
            await ctx.send(f"Updated this server's help category name")

    @commands.command(ignore_extra=False)
    @commands.check_any(
        commands.has_permissions(manage_guild=True),
        commands.has_any_role("Organizer", "Mentor"),
    )
    async def new(self, ctx):
        """Creates a new private help channel"""
        channel = await self.make_help_channel(ctx.guild, ctx.author)
        await channel.send(
            f"Created by {ctx.author.mention}."
            " Use `$add <username>` to add others into this channel."
            " Use `$leave` to leave this channel."
        )

    @commands.command(ignore_extra=False, require_var_positional=True)
    @commands.check_any(
        commands.has_permissions(manage_guild=True),
        commands.has_role("Organizer"),
        commands.check(is_help_channel_owner_check),
    )
    @commands.check(is_help_channel_check)
    async def add(self, ctx, *users: discord.Member):
        """Adds members into the current help channel"""
        # Add overrides for users specified
        for user in users:
            await ctx.channel.set_permissions(user, read_messages=True)
        # Mention the added users
        mentions = [user.mention for user in users]
        await ctx.channel.send(f"Added {', '.join(mentions)}")

    @commands.command(ignore_extra=False)
    @commands.check(is_help_channel_check)
    async def leave(self, ctx):
        """Removes you from the current help channel

        Note that the channel isn't deleted. Ask an organizer to do so (because
        history is important).

        """
        # Remove override for the user
        await ctx.channel.set_permissions(ctx.author, overwrite=None)
        # Mention the user that left
        await ctx.send(f"{ctx.author.mention} left :(")

    async def get_category_name(self, guild):
        """Return the help category name for the guild

        Defaults to "Help Channels"

        """
        return (
            await self.bot.store.get(f"help/category/{guild.id}")
            or "Help Channels"
        )

    async def set_category_name(self, guild, name):
        """Sets the help category name for the guild"""
        await self.bot.store.set(f"help/category/{guild.id}", name)

    async def get_channel_owner(self, channel):
        """Returns the user ID of the creator of this help channel

        If not found, a LookupError will be raised.

        """
        owner_id = await self.bot.store.get(f"help/owner/{channel.id}")
        if not owner_id:
            raise LookupError(f"could not get owner of {channel.id}")
        return int(owner_id)

    async def is_help_channel(self, channel):
        try:
            await self.get_channel_owner(channel)
        except LookupError:
            return False
        else:
            return True

    async def make_help_channel(self, guild, creator):
        """Makes and returns a new help channel

        This raises RuntimeError if the maximum number of channels in a server
        has been reached (for some reason).

        """
        # Increment channel count and get next channel name
        channel_count = int(
            await self.bot.store.get(f"help/channels/{guild.id}")
            or "0"
        )
        await self.bot.store.set(
            f"help/channels/{guild.id}",
            channel_count + 1,
        )
        channel_name = f"help-{channel_count + 1}"
        # Get root category name
        root_category_name = await self.get_category_name(guild)
        # Loop up category names from "name", "name 2", "name 3" upwards
        for suffix in range(1, 100):
            if suffix == 1:
                category_name = root_category_name
            else:
                category_name = f"{root_category_name} {suffix}"
            # Check if a category with that name exists
            for category in guild.categories:
                # Do a case insensitive check (Discord UI always shows uppercase)
                if category.name.upper() == category_name.upper():
                    break
            # If it doesn't, make one with that name
            else:
                category = await guild.create_category(
                    category_name,
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            read_messages=False,
                            connect=False
                        ),
                        guild.me: discord.PermissionOverwrite(
                            read_messages=True,
                            connect=True,
                        ),
                    },
                )
            # Try creating a channel in the category
            try:
                channel = await category.create_text_channel(channel_name)
            # We've reached the max number of channels in a category - continue
            except discord.HTTPException:
                continue
            # Set the owner id, make them able to view the channel, and return
            # the channel
            else:
                await self.bot.store.set(
                    f"help/owner/{channel.id}",
                    creator.id,
                )
                await channel.set_permissions(creator, read_messages=True)
                return channel
        # We've reached the max number of channels in a server!?
        raise RuntimeError("cannot create a new help channel")

def setup(bot):
    bot.add_cog(Help(bot))
