import dico_command


class Basic(dico_command.Addon):
    @dico_command.command("ping")
    async def ping(self, ctx: dico_command.Context):
        await ctx.reply(f"Pong! {round(self.bot.ping*1000)}ms")


def load(bot: dico_command.Bot):
    bot.load_addons(Basic)


def unload(bot: dico_command.Bot):
    bot.unload_addons(Basic)
