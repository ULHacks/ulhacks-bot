"""Provides utilities for having an up to date list of available moderators"""

import contextlib
import discord
from discord.ext import commands

class Moderators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def mods(self, ctx):
        """Command group for handling a message with available moderators"""
        raise commands.CommandNotFound("Please use a valid subcommand")

    @mods.command()
    async def create(self, ctx):
        """Creates a new message holding all available moderators"""
        # Create and update the message
        await self.create_message(ctx.channel)
        with contextlib.suppress(ValueError, LookupError):
            await self.update_message(ctx.guild)

    @mods.command()
    async def update(self, ctx):
        """Checks all members and update the message"""
        # Check all members
        for member in ctx.guild.members:
            await self.update_member(member)
        # Update the message
        await self.update_message(ctx.guild)
        # Notify that it's updated
        await ctx.send("Updated online moderators list")

    @mods.command()
    async def prefix(self, ctx, *, prefix=None):
        """Sets or gets the message prefix"""
        key = f"moderators/{ctx.guild.id}"
        if prefix is None:
            prefix = await self.bot.store.get(f"{key}/prefix")
            await ctx.send(f"This server's mods message prefix is: {prefix}")
        else:
            if prefix == '""':
                prefix = ""
            await self.bot.store.set(f"{key}/prefix", prefix)
            await ctx.send(f"Updated this server's mods message prefix")
            # Update just in case
            with contextlib.suppress(ValueError, LookupError):
                await self.update_message(ctx.guild)

    @mods.command()
    async def roles(self, ctx, *, roles=None):
        """Sets or gets the moderator role names

        Note that you should use role names separated by spaces, not role
        mentions, IDs, or separated by commas.

        """
        key = f"moderators/{ctx.guild.id}"
        if roles is None:
            roles = await self.bot.store.get(f"{key}/roles")
            await ctx.send(f"This server's mod roles are: {roles}")
        else:
            if roles == '""':
                roles = ""
            await self.bot.store.set(f"{key}/roles", roles)
            await ctx.send(f"Updated this server's mod roles")
            # Update just in case
            with contextlib.suppress(ValueError, LookupError):
                await self.update_message(ctx.guild)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await self.update_member(after)
        with contextlib.suppress(ValueError, LookupError):
            await self.update_message(after.guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.update_member(member)
        with contextlib.suppress(ValueError, LookupError):
            await self.update_message(member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.remove_member(member)
        with contextlib.suppress(ValueError, LookupError):
            await self.update_message(member.guild)

    async def update_member(self, member):
        """Updates the store with the member's status"""
        key = f"moderators/{member.guild.id}"
        # Ignore if not a moderator
        raw_role_names = await self.bot.store.get(f"{key}/roles")
        role_names = {name.upper() for name in raw_role_names.split()}
        if not any(role.name.upper() in role_names for role in member.roles):
            return
        # Update online members
        online_ids = {*(await self.bot.store.get(f"{key}/online")).split()}
        if member.status == discord.Status.online:
            online_ids.add(str(member.id))
        else:
            online_ids.discard(str(member.id))
        await self.bot.store.set(f"{key}/online", " ".join(online_ids))

    async def remove_member(self, member):
        """Removes the member from the store"""
        key = f"moderators/{member.guild.id}"
        # Update online members
        online_ids = {*(await self.bot.store.get(f"{key}/online")).split()}
        online_ids.discard(str(member.id))
        await self.bot.store.set(f"{key}/online", " ".join(online_ids))

    async def create_message(self, channel):
        """Creates the message and updates to the store"""
        key = f"moderators/{channel.guild.id}"
        await self.bot.store.set(f"{key}/channel", channel.id)
        message = await channel.send(
            "*Loading...*",
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await self.bot.store.set(f"{key}/message", message.id)

    async def update_message(self, guild):
        """Updates the message from the store"""
        key = f"moderators/{guild.id}"
        # Get message prefix
        prefix = await self.bot.store.get(f"{key}/prefix")
        if prefix:
            prefix += " "
        # Create string with mentions
        online_ids = {*(await self.bot.store.get(f"{key}/online")).split()}
        if online_ids:
            mentions = ", ".join(f"<@{id}>" for id in sorted(online_ids))
        else:
            mentions = "*No one is online :(*"
        # Get the channel
        channel_id = int(await self.bot.store.get(f"{key}/channel"))
        channel = guild.get_channel(channel_id)
        if channel is None:
            raise LookupError(f"cannot get channel with id: {channel_id}")
        # Get the message
        message_id = int(await self.bot.store.get(f"{key}/message"))
        partial_message = channel.get_partial_message(message_id)
        # Edit the message
        try:
            await partial_message.edit(content=f"{prefix}{mentions}")
        except discord.NotFound as e:
            error = f"cannot get message with id: {message_id}"
            raise LookupError(error) from e

def setup(bot):
    bot.add_cog(Moderators(bot))
