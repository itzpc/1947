import coc
import discord
import asyncio
from datetime import datetime
from application.constants.guildsupport import GuildSupport
from application.constants.bot_const import BotVariables
from application.database.db_utlis import DbUtlis



class BotActions():
    def __init__(self, bot,connection):
        self.bot = bot
        self.db = DbUtlis(connection)
    async def online_message(self):
        status_channel = self.bot.get_channel(GuildSupport.BOT_STATUS_CHANNEL_ID)
        last_msg=await status_channel.fetch_message(status_channel.last_message_id)
        bot_info = await self.db.get_bot_info(BotVariables.BOT_ID)
        title = "BOT is Online"
        description = f"Info"
        last_down_time = bot_info['last_down_time']
        now = datetime.utcnow()
        time_diff = now-last_down_time
        duration = time_diff/60 
        
        embed = discord.Embed(title=title,description=description,color=discord.Color.green()) 
        embed.add_field(name="Bot Owner", value=f"Pc")
        embed.add_field(name="Last Down time", value=last_down_time, inline=True)
        embed.add_field(name="Last Down Duration", value=f"Lasted {duration.seconds} seconds", inline=True)
        embed.add_field(name="Up Time", value=f"About {time_diff.days} days", inline=True)
        embed.add_field(name="Last Periodic Check", value=bot_info['last_check'], inline=True)
        #embed.add_field(name="Bot Version", value=f"{self.bot.version}" )
        embed.add_field(name="Discord Version", value=f"{discord.__version__}" )
        embed.add_field(name="COC Version", value=f"{coc.__version__}" )
        embed.add_field(name="# Servers", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="# Users", value=f"{len(self.bot.users)}", inline=True)
        #embed.add_field(name="# Clans", value=f"", inline=True)
        #embed.add_field(name="# Linked Players", value=f"" ,inline=True)
        
        await last_msg.edit(embed=embed)
    async def offline_message(self):
        await self.db.update_last_down_time_bot_info(BotVariables.BOT_ID,datetime.utcnow())
        status_channel = self.bot.get_channel(GuildSupport.BOT_STATUS_CHANNEL_ID)
        last_msg=await status_channel.fetch_message(status_channel.last_message_id)
        title = "BOT is Offline"
        embed = discord.Embed(title=title,color=discord.Color.red()) 
        await last_msg.edit(embed=embed)
        
    
