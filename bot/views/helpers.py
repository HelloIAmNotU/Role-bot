import discord
from discord import ui

#standard embed view for sending messages with the bot
class EmbedView(ui.LayoutView):
    def __init__(self, *, myText: str) -> None:
        super().__init__(timeout=None)
        self.text = ui.TextDisplay(myText)
        container = ui.Container(self.text, accent_color=discord.Color.red())
        self.add_item(container)