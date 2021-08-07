"""Provides Discord commands to the key-value storage"""

from discord.ext import commands

class Paginator:
    def __init__(self, sep=", ", limit=2000):
        self.sep = sep
        self.limit = limit
        self.buffer = []
        self.length = 0

    def add(self, string):
        if len(string) > self.limit:
            raise ValueError("added string too large for paginator")
        if not self.length + len(self.sep) + len(string) > self.limit:
            self.buffer.append(string)
            self.length += len(self.sep) + len(string)
            return None
        result = self.sep.join(self.buffer)
        self.buffer = [string]
        self.length = len(string)
        return result

    def flush(self):
        if not self.buffer:
            return None
        result = self.sep.join(self.buffer)
        self.buffer = []
        self.length = 0
        return result

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
        paginator = Paginator()
        async for key in self.bot.store.keys():
            if page := paginator.add(key):
                await ctx.send(page)
        if page := paginator.flush():
            await ctx.send(page)

def setup(bot):
    bot.add_cog(StoreCog(bot))
