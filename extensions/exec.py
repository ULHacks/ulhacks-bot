"""Provides an exec command for the owner only

Adapted from JoshGone's admin.py

"""
import ast
from discord.ext import commands

class Exec(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.result = None

    def ensure_scope(self):
        # Ensures that the bot has an execution scope
        if not hasattr(self.bot, "scope"):
            # Initialize the scope with some modules and the bot
            import asyncio
            import discord
            self.bot.scope = {
                "bot": self.bot,
                "asyncio": asyncio,
                "discord": discord,
                "commands": commands,
            }

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

    @commands.command(hidden=True)
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
                header="async def ____thingy(ctx, _): pass",
                filename="<discordexec>",
            )
        except Exception as e:
            raise RuntimeError(f"Error preparing code: {e!r}") from e
        # Await and send its result
        result = await func(ctx, self.result)
        if result is not None:
            self.result = result
            await ctx.send(content=str(result) or "*Empty string*")
        else:
            await ctx.send("*Finished*")

def setup(bot):
    bot.add_cog(Exec(bot))
