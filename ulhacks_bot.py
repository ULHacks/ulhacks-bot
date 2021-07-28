"""Entry point to the ULHacks Bot"""

import os
from discord.ext import commands

command_prefix = commands.when_mentioned_or("$")

def run(token, **bot_kwargs):
    bot = commands.Bot(**bot_kwargs)

    @bot.command()
    async def hi(ctx):
        await ctx.send("hi")

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

    bot.run(token)

if __name__ == "__main__":
    run(
        os.environ["ULHACKS_BOT_TOKEN"],
        command_prefix=command_prefix,
    )
