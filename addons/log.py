import datetime

import dico
import dico_command


class Log(dico_command.Addon):
    @dico_command.on("message_update")
    async def on_message_edit(self, message: dico.MessageUpdate):
        if message.guild_id != 832488748843401217:
            return
        if message.content == message.original.content:
            return
        embed = dico.Embed(title="Message Edited",
                           description=f"{message.author.mention} edited a message in {message.channel.mention}",
                           timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Before", value=message.original.content, inline=False)
        embed.add_field(name="After", value=message.content, inline=False)
        # embed.add_field(name="URL", value=message.)
        await self.bot.create_message(832565224955314177, embed=embed)

    @dico_command.on("message_delete")
    async def on_message_delete(self, message_delete: dico.MessageDelete):
        if message_delete.guild_id != 832488748843401217:
            return
        embed = dico.Embed(title="Message Deleted",
                           description=f"{message_delete.message.author.mention} deleted a message in {message_delete.channel.mention}",
                           timestamp=datetime.datetime.utcnow(),
                           color=0xe74c3c)
        embed.add_field(name="Content", value=message_delete.message.content, inline=False)
        await self.bot.create_message(832565224955314177, embed=embed)


def load(bot: dico_command.Bot):
    bot.load_addons(Log)


def unload(bot: dico_command.Bot):
    bot.unload_addons(Log)
