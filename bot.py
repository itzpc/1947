# pip libraries
import discord
from discord.ext import commands
# Inbuilt Libraries
from datetime import datetime
import logging
import os
import aiohttp
import asyncio
import sys, traceback
# userDefined
from application.config.config import DiscordConfig
from application.constants.guild1947 import Guild1947
from application.cogs.utlis.context import Context

class BotInitialization():

    @staticmethod
    def get_prefix(bot,message):
        prefixes = DiscordConfig.PREFIX
        if not message.guild:
            return '1947'
        return commands.when_mentioned_or(*prefixes)(bot, message)

    @staticmethod
    def process_command(ctx,message,guild,channel):
        if ctx.command :
            if message.guild.id in guild:
                if message.channel.id in channel:
                    return True
        return False

class Bot1947(commands.AutoShardedBot):

    def __init__(self,coc_client):
        self.bot_init = BotInitialization()
        self.coc = coc_client
        super().__init__(command_prefix=self.bot_init.get_prefix, description=DiscordConfig.DESCRIPTION)
        self.owner_id = DiscordConfig.BOT_OWNER_ID
        self.channel_id = DiscordConfig.ALLOWED_CHANNELS
        self.guild_id = DiscordConfig.ALLOWED_GUILDS
        self._task = self.loop.create_task(self.initialize())
        self.activity = discord.Activity(type=discord.ActivityType.listening, name='1947')
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
        if self.bot_init.process_command(ctx,message,self.guild_id, self.channel_id):
            await self.invoke(ctx)
        else:
            return 
    
    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_ready(self):
        print(f'Ready...!')

    async def on_resumed(self):
        print('resumed...')
    
    async def close(self):
        await super().close()
        await self.session.close()
        self._task.cancel()
        print(f'BOT is offline')
    
    def run(self):
        try:
            super().run(DiscordConfig.TOKEN,bot=True, reconnect=True)
        except Exception as e:
            print(f'Troubles running the bot!\nError: {e}')
            traceback.print_exc()    
