import types
import traceback

import dico
import dico_command

from dico import utils


class Debug(dico_command.Addon):
    @dico_command.command("eval")
    @dico_command.checks(lambda x: x.author.id == 288302173912170497)
    async def eval_command(self, ctx: dico_command.Context, *, original_code: str):
        msg = await ctx.reply("Please wait...")
        if original_code.startswith("```py") and original_code.endswith("```"):
            original_code = original_code.lstrip("```py\n")
            original_code = original_code.rstrip('```')
        if len(original_code.split('\n')) == 1 and not original_code.startswith("return"):
            original_code = f"return {original_code}"
        code = '\n'.join([f'    {x}' for x in original_code.split('\n')])
        code = f"async def execute_this(self, ctx):\n{code}"
        exec(compile(code, "<string>", "exec"))
        func = eval("execute_this")(self, ctx)
        embed = dico.Embed(title="dico EVAL", color=utils.rgb(225, 225, 225), timestamp=ctx.timestamp, display_footer=True)
        embed.add_field(name="Input", value=f"```py\n{original_code}\n```", inline=False)
        try:
            if isinstance(func, types.AsyncGeneratorType):
                await msg.delete()
                embed.add_field(name="Response", value="Generator results will separately be sent.", inline=False)
                msg = await ctx.reply(embed=embed)
                count = 0
                async for x in func:
                    count += 1
                    yield_embed = dico.Embed(title=f"yield #{count}", description=f"""```py\n{f'"{x}"' if isinstance(x, str) else x}\n```""")
                    yield_embed.add_field(name="Type", value=f"```py\n{type(x)}\n```")
                    await msg.reply(embed=yield_embed)
            else:
                res = await func
                await msg.delete()
                embed.add_field(name="Response", value=f"""```py\n{f'"{res}"' if isinstance(res, str) else res}\n```""", inline=False)
                embed.add_field(name="Type", value=f"```py\n{type(res)}\n```", inline=False)
                await ctx.reply(embed=embed)
        except Exception as ex:
            await msg.delete()
            tb = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
            tb = ("..." + tb[-1997:]) if len(tb) > 2000 else tb
            embed.color = 0xe74c3c
            embed.add_field(name="Traceback", value=f"```py\n{tb}\n```", inline=False)
            await ctx.reply(embed=embed)


def load(bot: dico_command.Bot):
    bot.load_addons(Debug)


def unload(bot: dico_command.Bot):
    bot.unload_addons(Debug)
