import discord
from discord import app_commands
from discord.ext import commands
from utils.db import db
from views.helpers import EmbedView

class Roles(commands.Cog):
    group = app_commands.Group(name="message",description="Functionality for role messages")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @group.command(name="create",description="ADMINS ONLY: Creates a role message that can be reacted to")
    async def create(self, interaction: discord.Interaction, emoji: str, role: discord.Role):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(view=EmbedView(myText="This command is reserved for an administrator"),ephemeral=True)
        
        try:
            await db.connect()
            record = await db.execute("SELECT * FROM messages WHERE guild_id = $1;",interaction.guild_id)
            await db.close()
        except:
            return await interaction.response.send_message(view=EmbedView(myText="Unable to access to database"),ephemeral=True)
        
        if len(record) != 0:
            return await interaction.response.send_message(view=EmbedView(myText="There is already a role message in this server. Try using /message add."),ephemeral=True)
        
        string = f"React with the following emojis to get the following roles!\n{emoji} - {role.mention}"
        msg = await interaction.channel.send(view=EmbedView(myText=string))

        try:
            await db.connect()
            await db.execute("INSERT INTO messages (guild_id, message_id, message_content, emojis, role_ids) VALUES ($1, $2, $3, $4, $5);", interaction.guild_id, msg.id, string, [emoji], [role.id])
            await db.close()
        except:
            return await interaction.response.send_message(view=EmbedView(myText="Unable to add message to database"),ephemeral=True)
        
        return await interaction.response.send_message(view=EmbedView(myText="Success!"),ephemeral=True)
    

    @group.command(name="add",description="ADMINS ONLY: Add a role to the react message")
    async def add(self, interaction: discord.Interaction, emoji: str, role: discord.Role):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(view=EmbedView(myText="This command is reserved for an administrator"),ephemeral=True)
        
        try:
            await db.connect()
            record = await db.execute("SELECT * FROM messages WHERE guild_id = $1;",interaction.guild_id)
            await db.close()
        except:
            return await interaction.response.send_message(view=EmbedView(myText="Unable to access to database"),ephemeral=True)
        
        if len(record) == 0:
            return await interaction.response.send_message(view=EmbedView(myText="There is no role message in this server."),ephemeral=True)
        
        roles = record[0]["role_ids"]
        emojis = record[0]["emojis"]

        if len(roles) >= 9:
            return await interaction.response.send_message(view=EmbedView(myText="You cannot add more roles to this message."),ephemeral=True)
        
        if emoji in emojis:
            return await interaction.response.send_message(view=EmbedView(myText="This emoji is already used."),ephemeral=True)
        
        roles.append(role.id)
        emojis.append(emoji)
        msg = await interaction.channel.fetch_message(record[0]["message_id"])
        string = record[0]["message_content"]
        string += f"\n{emoji} - {role.mention}"

        await msg.edit(view=EmbedView(myText=string))

        try:
            await db.connect()
            await db.execute("DELETE FROM messages WHERE guild_id = $1", interaction.guild.id)
            await db.execute("INSERT INTO messages (guild_id, message_id, message_content, emojis, role_ids) VALUES ($1, $2, $3, $4, $5);", interaction.guild_id, msg.id, string, emojis, roles)
            await db.close()
        except:
            return await interaction.response.send_message(view=EmbedView(myText="Unable to add message to database"),ephemeral=True)
        
        return await interaction.response.send_message(view=EmbedView(myText="Success!"),ephemeral=True)
    

    @group.command(name="delete",description="ADMINS ONLY: Deletes the role string")
    async def delete(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(view=EmbedView(myText="This command is reserved for an administrator"),ephemeral=True)
        
        try:
            await db.connect()
            record = await db.execute("SELECT * FROM messages WHERE guild_id = $1;",interaction.guild_id)
            await db.close()
        except:
            return await interaction.response.send_message(view=EmbedView(myText="Unable to access to database"),ephemeral=True)
        
        if len(record) == 0:
            return await interaction.response.send_message(view=EmbedView(myText="There is no role message in this server."),ephemeral=True)
        
        
        msg = await interaction.channel.fetch_message(record[0]["message_id"])
        await msg.delete()

        try:
            await db.connect()
            await db.execute("DELETE FROM messages WHERE guild_id = $1", interaction.guild.id)
            await db.close()
        except:
            return await interaction.response.send_message(view=EmbedView(myText="Unable to delete message from database"),ephemeral=True)
        
        return await interaction.response.send_message(view=EmbedView(myText="Success!"),ephemeral=True)
    

    async def react(self, payload: discord.RawReactionActionEvent):
        try:
            await db.connect()
            record = await db.execute("SELECT * FROM messages WHERE guild_id = $1;", payload.guild_id)
            await db.close()
        except:
            return
        
        if payload.message_id != record[0]["message_id"]:
            return
        
        index = -1
        for i in range(len(record[0]["emojis"])):
            if record[0]["emojis"][i] == payload.emoji.name:
                index = i
                break
        if index == -1:
            return
        
        try:
            role = payload.member.guild.get_role(record[0]["role_ids"][index])
            return await payload.member.add_roles(role)
        except:
            return
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roles(bot))