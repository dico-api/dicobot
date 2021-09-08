import re

import dico
import dico_command

from dico import utils

from module.cursor import Cursor


class Music(dico_command.Addon):
    def verify_voice_state(self, voice_state: dico.VoiceState, *, check_connected: bool = False, check_playing: bool = False, check_paused: bool = False):
        if not voice_state or not voice_state.channel_id:
            return "Please connect or reconnect to the voice channel first."

        player = self.bot.lava.player_manager.get(int(voice_state.guild_id))

        if check_connected and player is None:
            return 2, "Please play any music first."

        if check_playing and player.paused:
            return 3, "Player is paused. Please resume the player first."

        if check_paused and not player.paused:
            return 4, "Player is currently playing. Please pause the player first."
        return None

    @dico_command.command("connect")
    async def connect(self, ctx: dico_command.Context):
        voice_state = ctx.author.voice_state
        vv = self.verify_voice_state(voice_state)
        if vv:
            return await ctx.reply(embed=dico.Embed(description=vv, color=0xe74c3c))
        msg = await ctx.reply(embed=dico.Embed(description="Please wait, connecting..."))
        self.bot.lava.player_manager.create(int(ctx.guild_id), region="ko")
        await self.bot.update_voice_state(ctx.guild_id, voice_state.channel_id)
        await msg.edit(embed=dico.Embed(description="Successfully connected to voice channel!", color=0x3dd415))

    @dico_command.command("disconnect")
    async def disconnect(self, ctx: dico_command.Context):
        msg = await ctx.reply(embed=dico.Embed(description="Please wait, disconnecting..."))
        await self.bot.update_voice_state(ctx.guild_id)
        await msg.edit(embed=dico.Embed(description="Successfully disconnected from voice channel!", color=0x3dd415))
        player = self.bot.lava.player_manager.get(int(ctx.guild_id))
        if player:
            await self.bot.lava.player_manager.destroy(ctx.guild_id)

    @dico_command.command("play")
    async def play(self, ctx: dico_command.Context, *, url: str):
        voice_state = ctx.author.voice_state
        vv = self.verify_voice_state(voice_state)
        if vv:
            return await ctx.reply(embed=dico.Embed(description=vv, color=0xe74c3c))
        if not re.match("https?://(?:www\.)?.+", url):
            url = f"ytsearch:{url}"
        player = self.bot.lava.player_manager.get(int(ctx.guild_id))
        if not player:
            return await ctx.reply(embed=dico.Embed(description="Please run `!connect` first.", color=0xe74c3c))
        resp = await player.node.get_tracks(url)
        if resp is None or len(resp["tracks"]) == 0:
            return await ctx.reply(embed=dico.Embed(description="Unable to find any song.", color=0xe74c3c))
        msg = await ctx.reply(embed=dico.Embed(description="Found the music, please wait..."))
        track = None
        if resp["loadType"] == "PLAYLIST_LOADED":
            return await msg.edit(embed=dico.Embed(description="Sorry, playlist is not supported.", color=0xe74c3c))
        elif resp["loadType"] == "SEARCH_RESULT":
            await msg.delete()
            tracks = resp["tracks"]
            base_embed = dico.Embed(title=f"YouTube Search Result - Total {len(tracks)}", color=utils.rgb(225, 225, 225))
            items = [f"[{x['info']['title']}]({x['info']['uri']})" for x in tracks]
            cursor = Cursor(self.bot, ctx, items, base_embed, extra_button=dico.Button(style=dico.ButtonStyles.PRIMARY, label="Information", custom_id="info"))
            async for interaction, num in cursor.start_as_generator():
                track = tracks[num]
                embed = dico.Embed(title=f"Track Information - {track['info']['title']}")
                embed.add_field(name="Uploaded By", value=track["info"]["author"], inline=False)
                embed.add_field(name="URL", value=track["info"]["uri"], inline=False)
                embed.set_image(url=f"https://img.youtube.com/vi/{track['info']['identifier']}/hqdefault.jpg")
                await interaction.create_followup_message(embed=embed, ephemeral=True)
            _msg, resp = cursor.result
            await _msg.delete()
            if resp is None:
                return await ctx.reply(embed=dico.Embed(description="Canceled player.", color=0xe74c3c))
            msg = await ctx.reply(embed=dico.Embed(description="Please wait, preparing...", color=utils.rgb(225, 225, 225)))
            track = tracks[resp]
        track = track or resp['tracks'][0]
        player.add(requester=int(ctx.author.id), track=track)
        if not player.is_playing:
            await player.play()
            await msg.edit(embed=dico.Embed(description=f"Playing [{track['info']['title']}]({track['info']['uri']}).", color=0x3dd415))
        else:
            await msg.edit(embed=dico.Embed(description=f"Added [{track['info']['title']}]({track['info']['uri']}) to queue.", color=0x3dd415))

    @dico_command.command("skip")
    async def skip(self, ctx: dico_command.Context):
        voice_state = ctx.author.voice_state
        vv = self.verify_voice_state(voice_state, check_connected=True, check_playing=True)
        if vv:
            return await ctx.reply(embed=dico.Embed(description=vv, color=0xe74c3c))
        player = self.bot.lava.player_manager.get(int(ctx.guild_id))
        msg = await ctx.reply(embed=dico.Embed(description="Skipping this music..."))
        await player.skip()
        await msg.edit(embed=dico.Embed(description="Done skipping!", color=0x3dd415))

    @dico_command.command("loop")
    async def loop(self, ctx: dico_command.Context):
        voice_state = ctx.author.voice_state
        vv = self.verify_voice_state(voice_state, check_connected=True)
        if vv:
            return await ctx.reply(embed=dico.Embed(description=vv, color=0xe74c3c))
        player = self.bot.lava.player_manager.get(int(ctx.guild_id))
        player.set_repeat(not player.repeat)
        await ctx.reply(embed=dico.Embed(description=f"Repeat is now {'enabled' if player.repeat else 'disabled'}.", color=0x3dd415))

    @dico_command.command("shuffle")
    async def shuffle(self, ctx: dico_command.Context):
        voice_state = ctx.author.voice_state
        vv = self.verify_voice_state(voice_state, check_connected=True)
        if vv:
            return await ctx.reply(embed=dico.Embed(description=vv, color=0xe74c3c))
        player = self.bot.lava.player_manager.get(int(ctx.guild_id))
        player.set_shuffle(not player.shuffle)
        await ctx.reply(embed=dico.Embed(description=f"Shuffle is now {'enabled' if player.shuffle else 'disabled'}.", color=0x3dd415))

    @dico_command.command("volume")
    async def volume(self, ctx, vol: int = None):
        voice_state = ctx.author.voice_state
        vv = self.verify_voice_state(voice_state, check_connected=True, check_playing=True)
        if vv:
            return await ctx.reply(embed=dico.Embed(description=vv, color=0xe74c3c))
        player = self.bot.lava.player_manager.get(int(ctx.guild_id))
        if not vol:
            return await ctx.reply(embed=dico.Embed(description=f"Current volume is `{player.volume}`%.", color=utils.rgb(225, 225, 225)))
        vol = int(vol)
        if not 0 < vol <= 1000:
            return await ctx.reply(embed=dico.Embed(description="Volume must be between 1 and 1000.", color=0xe74c3c))
        await player.set_volume(vol)
        await ctx.reply(embed=dico.Embed(description=f"Volume is now set to `{vol}`%.", color=0x3dd415))


def load(bot: dico_command.Bot):
    bot.load_addons(Music)


def unload(bot: dico_command.Bot):
    bot.unload_addons(Music)
