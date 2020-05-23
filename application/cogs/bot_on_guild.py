import coc 
import discord
from discord.ext import commands
from application.constants.emoji import Emoji
from application.database.db_utlis import DbUtlis
from application.constants.guildsupport import GuildSupport
import logging

class BotOnGuild(commands.Cog):
    """Cog for various events and debugging"""
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.initialize())
        self.db = DbUtlis(self.bot.postgre_db)
    def cog_unload(self):
        self.task.cancel()
        self.bot.coc.remove_events(self.on_event_error)

    async def initialize(self):
        await self.bot.wait_until_ready()

    
    def get_join_channel(self):
        return self.bot.get_guild(GuildSupport.SERVER_ID).get_channel(GuildSupport.BOT_JOIN_CHANNEL_ID)
    
    def get_leave_channel(self):
        return self.bot.get_guild(GuildSupport.SERVER_ID).get_channel(GuildSupport.BOT_LEAVE_CHANNEL_ID)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.db.insert_into_bot_table(guild.id)
        join_channel = self.get_join_channel()
        title = "Joined a server"
        description = f"Info"
        
        embed = discord.Embed(title=title,description=description,color=discord.Color.green()) 
        embed.add_field(name="Name", value=f"{guild.name}", inline=True)
        embed.add_field(name="ID", value=f"{guild.id}", inline=True)
        embed.add_field(name="# Users", value=f"{len(guild.members)}", inline=True)
        await join_channel.send(embed=embed)
        logging.info(f"JOINED A SERVER - {guild.id}")
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.db.delete_from_bot_table(guild.id)
        leave_channel = self.get_leave_channel()
        title = "Left a server"
        description = f"Info"
        
        embed = discord.Embed(title=title,description=description,color=discord.Color.red()) 
        embed.add_field(name="Name", value=f"{guild.name}", inline=True)
        embed.add_field(name="ID", value=f"{guild.id}", inline=True)
        embed.add_field(name="# Users", value=f"{len(guild.members)}", inline=True)
        await leave_channel.send(embed=embed)
        logging.info(f"LEFT A SERVER - {guild.id}")
def setup(bot):
    bot.add_cog(BotOnGuild(bot))
