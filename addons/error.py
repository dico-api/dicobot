import traceback

import dico
import dico_command


class Error(dico_command.Addon):
    @dico_command.on("command_error")
    async def on_command_error(self, ctx: dico_command.Context, ex: Exception):
        embed = dico.Embed(title=f"Error while executing command {ctx.command.name}.", color=0xe74c3c, timestamp=ctx.timestamp)
        tb = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        edited_tb = ("..." + tb[-1985:]) if len(tb) > 2000 else tb
        embed.description = f"```py\n{edited_tb}\n```"
        await ctx.reply(embed=embed)


def load(bot: dico_command.Bot):
    bot.load_addons(Error)


def unload(bot: dico_command.Bot):
    bot.unload_addons(Error)
