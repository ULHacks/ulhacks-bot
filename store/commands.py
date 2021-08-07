"""Provides Discord commands to the key-value storage"""

from discord.ext import commands

class StoreCog(commands.Cog, name="Store"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(ignore_extras=False)
    @commands.is_owner()
    async def set(self, ctx, key, value):
        await self.bot.store.set(key, value)
        await ctx.send("Updated")

    @commands.command(ignore_extras=False)
    @commands.is_owner()
    async def get(self, ctx, key):
        value = await self.bot.store.get(key)
        await ctx.send(value or "*Empty value*")

def setup(bot):
    bot.add_cog(StoreCog(bot))
