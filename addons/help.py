import dico
import dico_command

from dico import utils


class Help(dico_command.Addon):
    @dico_command.command("help")
    async def help(self, ctx: dico_command.Context):
        embed = dico.Embed(title="dico Help Command",
                           description=f"Powered by dico library dev version {dico.__version__} and dico-command {dico_command.__version__}, "
                                       f"music powered by Lavalink.",
                           timestamp=ctx.timestamp,
                           color=utils.rgb(225, 225, 225))
        embed.add_field(name=f"{ctx.prefix}help", value="Shows help command", inline=False)
        embed.add_field(name=f"{ctx.prefix}ping", value="Shows bot websocket ping.", inline=False)
        embed.add_field(name=f"{ctx.prefix}connect", value="Connects to voice channel.", inline=False)
        embed.add_field(name=f"{ctx.prefix}play [URL]", value="Plays music. Only accepts URL for now.", inline=False)
        embed.add_field(name=f"{ctx.prefix}skip", value="Skips current music.", inline=False)
        embed.add_field(name=f"{ctx.prefix}volume", value="Changes volume.", inline=False)
        embed.add_field(name=f"{ctx.prefix}disconnect", value="Disconnects from voice channel.", inline=False)
        embed.set_footer(text=str(ctx.member) if ctx.member else str(ctx.author),
                         icon_url=ctx.author.avatar_url())
        await ctx.reply(embed=embed)


def load(bot: dico_command.Bot):
    bot.load_addons(Help)


def unload(bot: dico_command.Bot):
    bot.unload_addons(Help)
