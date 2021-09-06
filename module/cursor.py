import asyncio
import math
import typing
import dico


class Cursor:
    def __init__(self,
                 client: dico.Client,
                 message: dico.Message,
                 items: typing.List[str],
                 base_embed: dico.Embed,
                 max_per_page: int = 5,
                 as_reply: bool = True,
                 mention_author: bool = True,
                 timeout: int = 30,
                 extra_button: dico.Button = None):  # Passing extra_button will enable async generator mode.
        self.client = client
        self.message = message
        self.items = items,
        self.base_embed = base_embed
        self.max_per_page = max_per_page
        self.as_reply = as_reply
        self.mention_author = mention_author
        self.timeout = timeout
        self.extra_button = extra_button

        self.next_item = dico.Button(style=dico.ButtonStyles.SECONDARY, label="Next Item", emoji={"id": None, "name": "⬇", "animated": False}, custom_id=f"next{message.id}")
        self.prev_item = dico.Button(style=dico.ButtonStyles.SECONDARY, label="Prev Item", emoji={"id": None, "name": "⬆", "animated": False}, custom_id=f"prev{message.id}")
        self.select = dico.Button(style=dico.ButtonStyles.SUCCESS, label="Select", emoji={"id": None, "name": "✅", "animated": False}, custom_id=f"select{message.id}")
        self.abort = dico.Button(style=dico.ButtonStyles.DANGER, label="Abort", emoji={"id": None, "name": "❌", "animated": False}, custom_id=f"abort{message.id}")
        __control_row = [self.prev_item, self.next_item, self.select, self.abort]
        if self.extra_button:
            __control_row.append(self.extra_button)
        self.control_row = dico.ActionRow(*__control_row)

        self.next_page = dico.Button(style=dico.ButtonStyles.SECONDARY, label="Next Page", emoji={"id": None, "name": "➡", "animated": False}, custom_id=f"npage{message.id}")
        self.prev_page = dico.Button(style=dico.ButtonStyles.SECONDARY, label="Prev Page", emoji={"id": None, "name": "⬅", "animated": False}, custom_id=f"ppage{message.id}")

        __custom_ids = ["next", "prev", "select", "abort", "npage", "ppage"]
        if self.extra_button:
            __custom_ids.append(self.extra_button.custom_id)
            self.extra_button.custom_id += str(message.id)
        self.custom_ids = [x+str(message.id) for x in __custom_ids]

        self.current_page = 0
        self.selected = 0
        self.page_index = 0
        self.pages = [[] for _ in range(math.ceil(len(items)/max_per_page))]

        self.result = ()

        for n, x in enumerate(items):
            self.pages[n//5].append(x)

    @property
    def page_row(self):
        cpage = dico.Button(style=dico.ButtonStyles.SECONDARY, label=f"Page {self.current_page+1}/{len(self.pages)}", custom_id="cpage", disabled=True)
        return dico.ActionRow(self.prev_page, cpage, self.next_page)

    @property
    def current_max(self):
        return len(self.pages[self.current_page]) - 1

    def run_next_item(self):
        self.selected += 1
        if self.page_index < self.current_max:
            self.page_index += 1
        else:
            self.page_index = 0
            if self.current_page == len(self.pages) - 1:
                self.current_page = 0
                self.selected = 0
            else:
                self.current_page += 1

    def run_prev_item(self):
        self.selected -= 1
        if self.page_index == 0:
            if self.current_page == 0:
                self.current_page = len(self.pages) - 1
                self.page_index = self.current_max
                self.selected = len(self.items) - 1
            else:
                self.current_page -= 1
                self.page_index = self.current_max
        else:
            self.page_index -= 1

    def run_next_page(self):
        self.page_index = 0
        if self.current_page == len(self.pages) - 1:
            self.current_page = 0
        else:
            self.current_page += 1
        self.selected = self.current_page*self.max_per_page

    def run_prev_page(self):
        self.page_index = 0
        if self.current_page == 0:
            self.current_page = len(self.pages) - 1
        else:
            self.current_page -= 1
        self.selected = self.current_page*self.max_per_page

    def event_check(self, interact: dico.Interaction):
        resp = interact.type.message_component and \
               interact.data.custom_id in self.custom_ids and\
               interact.guild_id == self.message.guild_id and \
               interact.channel_id == self.message.channel_id
        if interact.member and interact.member.user.id != self.message.author.id:
            self.client.loop.create_task(
                interact.create_response(dico.InteractionResponse(
                    dico.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                    dico.InteractionApplicationCommandCallbackData(content="This is not your session!", flags=64))
                )
            )
            return False
        return resp

    async def start(self):
        async for _ in self.start_as_generator():
            pass
        return self.result

    async def start_as_generator(self):
        msg = await self.message.reply("Please wait...", mention=self.mention_author)

        while True:
            embed = self.base_embed
            embed.fields = []
            [embed.add_field(name=("▶" if a == self.page_index else "")+f"#{a+1+(self.current_page*self.max_per_page)}", value=b, inline=False) for a, b in enumerate(self.pages[self.current_page])]
            msg = await msg.edit(content="", embed=embed, components=[self.control_row, self.page_row])
            try:
                interaction = await self.client.wait("interaction_create", check=self.event_check, timeout=self.timeout)
            except asyncio.TimeoutError:
                await msg.edit(components=[])
                self.result = (msg, None)
                break
            await interaction.create_response(dico.InteractionResponse(callback_type=dico.InteractionCallbackType.DEFERRED_UPDATE_MESSAGE, data={}))
            custom_id = interaction.data.custom_id
            if custom_id.startswith("next"):
                self.run_next_item()
            elif custom_id.startswith("prev"):
                self.run_prev_item()
            elif custom_id.startswith("npage"):
                self.run_next_page()
            elif custom_id.startswith("ppage"):
                self.run_prev_page()
            elif custom_id.startswith("select"):
                await msg.edit(components=[])
                self.result = (msg, self.selected)
                break
            elif custom_id.startswith("abort"):
                await msg.edit(components=[])
                self.result = (msg, None)
                break
            else:
                yield interaction, self.selected


async def start_cursor(client: dico.Client,
                       message: dico.Message,
                       items: typing.List[str],
                       base_embed: dico.Embed,
                       max_per_page: int = 5,
                       as_reply: bool = True,
                       mention_author: bool = True,
                       timeout: int = 30):
    pages = [[] for _ in range(math.ceil(len(items)/max_per_page))]

    for n, x in enumerate(items):
        pages[n//5].append(x)

    next_item = dico.Button(style=dico.ButtonStyles.SECONDARY, label="Next Item", emoji={"id": None, "name": "⬇", "animated": False}, custom_id=f"next{message.id}")
    prev_item = dico.Button(style=dico.ButtonStyles.SECONDARY, label="Prev Item", emoji={"id": None, "name": "⬆", "animated": False}, custom_id=f"prev{message.id}")
    select = dico.Button(style=dico.ButtonStyles.PRIMARY, label="Select", emoji={"id": None, "name": "✅", "animated": False}, custom_id=f"select{message.id}")
    abort = dico.Button(style=dico.ButtonStyles.DANGER, label="Abort", emoji={"id": None, "name": "❌", "animated": False}, custom_id=f"abort{message.id}")
    control_row = dico.ActionRow(prev_item, next_item, select, abort)

    next_page = dico.Button(style=dico.ButtonStyles.SECONDARY, label="Next Page", emoji={"id": None, "name": "➡", "animated": False}, custom_id=f"npage{message.id}")
    prev_page = dico.Button(style=dico.ButtonStyles.SECONDARY, label="Prev Page", emoji={"id": None, "name": "⬅", "animated": False}, custom_id=f"ppage{message.id}")

    custom_ids = [x+str(message.id) for x in ["next", "prev", "select", "abort", "npage", "ppage"]]

    current_page = 0
    selected = 0
    page_index = 0

    def check(interact: dico.Interaction):
        return interact.type.message_component and \
               interact.data.custom_id in custom_ids and\
               interact.guild_id == message.guild_id and \
               interact.channel_id == message.channel_id

    msg = await message.reply("Please wait...", mention=mention_author)

    while True:
        cpage = dico.Button(style=dico.ButtonStyles.SECONDARY, label=f"Page {current_page+1}/{len(pages)}", custom_id="cpage", disabled=True)
        page_row = dico.ActionRow(prev_page, cpage, next_page)
        # I forgot to add copy at Embed, so first reset the embed first.
        embed = base_embed
        embed.fields = []
        [embed.add_field(name=("▶" if a == page_index else "")+f"#{a+1+(current_page*max_per_page)}", value=b, inline=False) for a, b in enumerate(pages[current_page])]
        msg = await msg.edit(content="", embed=embed, components=[control_row, page_row])
        try:
            interaction = await client.wait("interaction_create", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            await msg.edit(components=[])
            return msg, None
        await interaction.create_response(dico.InteractionResponse(callback_type=dico.InteractionCallbackType.DEFERRED_UPDATE_MESSAGE, data={}))
        custom_id = interaction.data.custom_id

        current_max = len(pages[current_page]) - 1

        if custom_id.startswith("next"):
            selected += 1
            if page_index < current_max:
                page_index += 1
            else:
                page_index = 0
                if current_page == len(pages) - 1:
                    current_page = 0
                    selected = 0
                else:
                    current_page += 1
        elif custom_id.startswith("prev"):
            selected -= 1
            if page_index == 0:
                if current_page == 0:
                    current_page = len(pages) - 1
                    page_index = len(pages[current_page]) - 1
                    selected = len(items) - 1
                else:
                    current_page -= 1
                    page_index = len(pages[current_page]) - 1
            else:
                page_index -= 1
        elif custom_id.startswith("npage"):
            page_index = 0
            if current_page == len(pages) - 1:
                current_page = 0
            else:
                current_page += 1
            selected = current_page*max_per_page
        elif custom_id.startswith("ppage"):
            page_index = 0
            if current_page == 0:
                current_page = len(pages) - 1
            else:
                current_page -= 1
            selected = current_page*max_per_page
        elif custom_id.startswith("select"):
            await msg.edit(components=[])
            return msg, selected
        elif custom_id.startswith("abort"):
            await msg.edit(components=[])
            return msg, None
