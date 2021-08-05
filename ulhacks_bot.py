"""Entry point to the ULHacks Bot

For more info on why we have both a run and a _run function, see
https://github.com/GeeTransit/joshgone/blob/main/joshgone.py and its comments.

"""
import os
from discord.ext import commands

command_prefix = commands.when_mentioned_or("$")

def _run(token, **bot_kwargs):
    bot = commands.Bot(**bot_kwargs)

    bot.load_extension("extensions.info")
    bot.load_extension("extensions.admin")

    close = bot.loop.close
    bot.loop.close = lambda: None

    bot.run(token)

    bot.loop.close = close
    return bot.loop

def run(token, **bot_kwargs):
    """Runs the ULHacks Bot with the provided token and bot options"""
    loop = _run(token, **bot_kwargs)

    try:
        loop.call_later(0.1, loop.stop)
        loop.run_forever()
    finally:
        loop.close()

def main():
    """Entry point to run the ULHacks bot"""
    run(
        os.environ["ULHACKS_BOT_TOKEN"],
        command_prefix=command_prefix,
    )

if __name__ == "__main__":
    main()
