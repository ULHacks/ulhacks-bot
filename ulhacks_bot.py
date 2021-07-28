"""Entry point to the ULHacks Bot"""

import os
from discord.ext import commands

command_prefix = commands.when_mentioned_or("$")

def run(token, **bot_kwargs):
    bot = commands.Bot(**bot_kwargs)

    bot.load_extension("extensions.info")

    bot.run(token)

if __name__ == "__main__":
    run(
        os.environ["ULHACKS_BOT_TOKEN"],
        command_prefix=command_prefix,
    )
