import discord
import asyncio
from datetime import datetime
from application.constants.guildsupport import GuildSupport
from application.database.db_utlis import DbUtlis



class BotActions():
    def __init__(self, bot):
        self.bot = bot

    async def online_message(self):
        status_channel = self.bot.get_channel(GuildSupport.BOT_STATUS_CHANNEL_ID)
        last_msg=await status_channel.fetch_message(status_channel.last_message_id)
        title = "BOT is Online"
        description = f"Info"
        
        embed = discord.Embed(title=title,description=description,color=discord.Color.green()) 
        #embed.add_field(name="Bot Owner", value=f"", inline=True)
        embed.add_field(name="Bot Owner Name", value=f"Pc", inline=True)
        #embed.add_field(name="Bot Description", value=f"{self.bot.description}" )
        embed.add_field(name="# Servers", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="# Users", value=f"{len(self.bot.users)}", inline=True)
        #embed.add_field(name="# Clans", value=f"", inline=True)
        #embed.add_field(name="# Linked Players", value=f"" ,inline=True)
        await last_msg.edit(embed=embed)
    async def offline_message(self):
        status_channel = self.bot.get_channel(GuildSupport.BOT_STATUS_CHANNEL_ID)
        last_msg=await status_channel.fetch_message(status_channel.last_message_id)
        title = "BOT is Offline"
        embed = discord.Embed(title=title,color=discord.Color.red()) 
        await last_msg.edit(embed=embed)
        
    
