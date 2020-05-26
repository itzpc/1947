# pip libraries
import discord
import gspread
from discord.ext import commands
# Inbuilt Libraries
from datetime import datetime
import logging
import os
import aiohttp
import asyncio
import sys, traceback
# userDefined
from application.config.config import DiscordConfig,PostgreeDB_Config
from application.constants.guild1947 import Guild1947
from application.cogs.utlis.context import Context
from application.database.postgre_db import PostgreDB
from application.database.db_utlis import DbUtlis
from application.utlis.bot_actions import BotActions

class BotInitialization():

    @staticmethod
    async def get_prefix(bot,message):
        allowed_channels = await DbUtlis(bot.postgre_db).get_default_channel(message.guild.id)
        if allowed_channels:
            if message.channel.id in allowed_channels:
                prefixes=list()
                prefixes.append('')
                return commands.when_mentioned_or(*prefixes)(bot, message)
            
        return commands.when_mentioned(bot, message)

        '''
        if message.channel.id in DiscordConfig.ALLOWED_CHANNELS:
            
            prefixes=list()
            prefixes.append('')
            return commands.when_mentioned_or(*prefixes)(bot, message)
        else:
            
            prefixes=DiscordConfig.PREFIX
        return commands.when_mentioned(bot, message)
        '''
    @staticmethod
    async def process_command(ctx,message,guild,channel):
        if ctx.command :
            if ctx.guild:
                    return True
                    
                        
                
        return False

class Bot1947(commands.AutoShardedBot):

    def __init__(self,coc_client,connection):
        
        self.bot_init = BotInitialization()
        self.postgre_db=connection
        self.coc = coc_client
        self.version= "Beta Test Release - v1"
        super().__init__(command_prefix=self.bot_init.get_prefix, description=DiscordConfig.DESCRIPTION)
        self.owner_id = DiscordConfig.BOT_OWNER_ID
        self.channel_id = DiscordConfig.ALLOWED_CHANNELS
        self.guild_id = DiscordConfig.ALLOWED_GUILDS
        self._task = self.loop.create_task(self.initialize())
        self.activity = discord.Activity(type=discord.ActivityType.listening, name='1947')
        self.case_insensitive = True
        try:
            for extension in DiscordConfig.initial_extensions:
                self.load_extension(extension)
        except:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            logging.error(f"Failed to load extension {extension}.")
            traceback.print_exc()

    async def initialize(self):
        self.session = aiohttp.ClientSession(loop=self.loop)
        await self.wait_until_ready()
        self.owner = self.get_user(OWNER)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        process_command = await self.bot_init.process_command(ctx,message,self.guild_id, self.channel_id)
        if process_command:
            await self.invoke(ctx)
        else:
            return 
    
    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_ready(self):
        logging.info("BOT IS ONLINE")
        print(f'Ready...!')
        await BotActions(super(),self.postgre_db).online_message()

    async def on_resumed(self):
        logging.info("BOT RESUMED")
    
    async def close(self):
        await BotActions(super(),self.postgre_db).offline_message()
        self._task.cancel()
        await PostgreDB(PostgreeDB_Config.URI).close(self.postgre_db)
        await self.session.close()
        await super().close()
        print(f'BOT is offline')
        logging.info("BOT IS OFFLINE")
        
    
    def run(self):
        try:
            super().run(DiscordConfig.TOKEN,bot=True, reconnect=True)
        except Exception as e:
            print(f'Troubles running the bot!\nError: {e}')
            traceback.print_exc()    
