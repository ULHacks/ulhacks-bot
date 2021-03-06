"""Provides an exec command for the owner only

Adapted from JoshGone's admin.py

"""
import asyncio
import ast

import discord
from discord.ext import commands

class Exec(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.result = None

    def ensure_scope(self):
        # Ensures that the bot has an execution scope
        if not hasattr(self.bot, "scope"):
            # Initialize the scope with some modules and the bot
            self.bot.scope = {
                "bot": self.bot,
                "asyncio": asyncio,
                "discord": discord,
                "commands": commands,
            }

    @staticmethod
    def reload(name):
        """Helper function to reload the specified module"""
        import importlib
        importlib.invalidate_caches()
        module = importlib.import_module(name)
        return importlib.reload(module)

    async def move(self, new_store):
        """Helper function to move the current store's data into a new store"""
        import store.move
        old_store = self.bot.store
        try:
            self.bot.store = store.move.MoveStore(old_store, new_store)
            await asyncio.sleep(1)
            await self.bot.store.move()
            await asyncio.sleep(1)
        except Exception:
            self.bot.store = old_store
        else:
            self.bot.store = new_store

    async def copy(self, new_store):
        """Helper function to copy the current store's data into a new store"""
        async for key in self.bot.store.keys():
            value = await self.bot.store.get(key)
            await new_store.set(key, value)

    async def backup(self, ctx):
        """Helper function to send a JSON file with the current store's data"""
        import os
        import random
        import store.json
        filename = f"temp-json-store-{random.randint(1, 9999):0>4}.json"
        try:
            json_store = store.json.JsonStore(filename)
            await self.copy(json_store)
            await ctx.send(file=discord.File(filename))
        finally:
            await asyncio.to_thread(os.unlink, filename)

    @staticmethod
    def clean_code(text):
        """Remove backticks from a Discord message's content

        Examples:
            clean_code("`69420`") == "69420"
            clean_code("``69420``") == "69420"
            clean_code("```py\n69420\n```") == "69420"

        """
        # Check if the text is multiline or not
        if "\n" not in text.strip().replace("\r", "\n"):
            # It's a single line - remove wrapping backticks (up to 2)
            for _ in range(2):
                if len(text) >= 2 and text[0] == text[-1] == "`":
                    text = text[1:-1]
                else:
                    break
            return text
        # It's on multiple lines - remove wrapping code fences
        lines = text.splitlines(keepends=True)
        if lines[0].strip() != "```py":
            raise ValueError(fr"First line has to be \`\`\`py")
        if lines[-1].strip() != "```":
            raise ValueError(fr"Last line has to be \`\`\`")
        del lines[0]
        del lines[-1]
        text = "".join(lines)
        return text

    @staticmethod
    def return_last(body):
        """Returns a new body that tries to returns the last statement"""
        if body and isinstance(body[-1], ast.Expr):
            expr = body[-1].value
            return_ = ast.parse("return None").body[0]
            return_.value = expr
            return [*body[:-1], return_]
        return body

    @staticmethod
    def wrap_ast(
        body,
        *,
        scope=None,
        header="def ____thingy(): pass",
        returnlast=False,
        filename="<wrappedfunc>",
    ):
        """Returns a function by merging the header and body

        The filename is passed to the compile function. The scope is passed to
        the exec function.

        """
        if scope is None:
            scope = {}
        # Wrap the statements in a function definition (possibly async)
        module = ast.parse(header)
        function = module.body[0]
        function.body = body
        module.body = [function]
        # Compile and execute it in the provided scope
        code = compile(ast.fix_missing_locations(module), filename, "exec")
        exec(code, scope)
        # Return the defined function
        return scope[function.name]

    @commands.command(aliases=["$"], hidden=True)
    @commands.is_owner()
    async def exec(self, ctx, *, text=""):
        """Executes some code"""
        try:
            self.ensure_scope()
            # Remove backticks
            text = self.clean_code(text)
            # Compile and get a list of statements
            body = ast.parse(text).body
            # Ensure there's at least one statement
            if not body:
                body.append(ast.Pass())
            # Try to return the last expression
            body = self.return_last(body)
            # Wrap in an async function
            func = self.wrap_ast(
                body,
                scope=self.bot.scope,
                header="async def ____thingy(ctx, cog, _): pass",
                filename="<discordexec>",
            )
        except Exception as e:
            raise RuntimeError(f"Error preparing code: {e!r}") from e
        try:
            # Await and send its result
            result = await func(ctx, self, self.result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            await ctx.send(f"*Traceback printed:* `{e!r}`")
        else:
            if result is not None:
                self.result = result
                await ctx.send(content=str(result) or "*Empty string*")
            else:
                await ctx.send("*Finished*")

def setup(bot):
    bot.add_cog(Exec(bot))
