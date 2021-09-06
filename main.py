import os
import json
import logging

import dico
import dico_command
import lavalink

with open("config.json", "r", encoding="UTF-8") as f:
    config = json.load(f)

logger = logging.getLogger('dicobot')
logging.basicConfig(level=logging.DEBUG)  # DEBUG/INFO/WARNING/ERROR/CRITICAL
handler = logging.FileHandler(filename=f'dicobot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


bot = dico_command.Bot(config["token"], ["dico!", "야채!"], intents=dico.Intents.no_privileged())
bot.lava = lavalink.Client(user_id=846571345847648336)
bot.lava.add_node(host=config["lavahost"], port=config["lavaport"], password=config["lavapw"], region="ko")
bot.on("RAW", bot.lava.voice_update_handler)


@bot.on_ready
async def on_ready(ready: dico.Ready):
    print("READY event dispatched.")
    print(f"Guilds: {len(ready.guilds)}")


@bot.command("load")
@dico_command.checks(lambda x: x.author.id == 288302173912170497)
async def load(ctx: dico_command.Context, name: str):
    bot.load_module(f"addons.{name}")
    await ctx.reply("Done!")


@bot.command("unload")
@dico_command.checks(lambda x: x.author.id == 288302173912170497)
async def unload(ctx: dico_command.Context, name: str):
    bot.unload_module(f"addons.{name}")
    await ctx.reply("Done!")


@bot.command("reload")
@dico_command.checks(lambda x: x.author.id == 288302173912170497)
async def reload(ctx: dico_command.Context, name: str):
    bot.reload_module(f"addons.{name}")
    await ctx.reply("Done!")


[bot.load_module(f"addons.{x.replace('.py', '')}") for x in os.listdir("./addons") if x.endswith('.py') and not x.startswith("_")]
bot.run()
