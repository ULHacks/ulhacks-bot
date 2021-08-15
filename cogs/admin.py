"""Owner only stuff like reloading extensions

Adapted from JoshGone's admin.py

"""
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, name: str):
        self.bot.load_extension(name)
        await ctx.send("Extension loaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, name: str):
        self.bot.unload_extension(name)
        await ctx.send("Extension unloaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, name: str):
        self.bot.reload_extension(name)
        await ctx.send("Extension reloaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def loaded(self, ctx):
        extensions = ", ".join(self.bot.extensions)
        await ctx.send(f"Extensions loaded: [{extensions}]")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting bot shut down.")
        await self.bot.close()

def setup(bot):
    bot.add_cog(Admin(bot))
