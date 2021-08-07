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

    @commands.command(ignore_extras=False)
    @commands.is_owner()
    async def keys(self, ctx):
        buffer = []
        length = 0
        sep = ", "
        async for key in self.bot.store.keys():
            if length + len(sep) + len(key) > 2000:
                await ctx.send(sep.join(buffer))
                buffer = [key]
                length = len(key)
            else:
                buffer.append(key)
                length += len(sep) + len(key)
        if buffer:
            await ctx.send(sep.join(buffer))

def setup(bot):
    bot.add_cog(StoreCog(bot))
