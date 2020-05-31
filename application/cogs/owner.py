import coc 
import os
import io
import discord
import textwrap
from contextlib import redirect_stdout
import logging
import asyncio
import traceback
from collections import Counter
from discord.ext import commands
from application.constants.emoji import Emoji
from application.database.db_utlis import DbUtlis
from application.constants.bot_const import *
from application.statics.prepare_message import PrepMessage
from application.constants.guildsupport import GuildSupport
from application.constants.bot_const import BotFiles,BotFiles
from application.statics.war_action import WarAction
from .utlis.image_maker import ImageMaker

class Owner(commands.Cog):
    """Commands for Only PC"""

    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.initialize())
        self.db = DbUtlis(self.bot.postgre_db)
        self._last_result = None

    def cog_unload(self):
        self.task.cancel()
        self.bot.coc.remove_events(self.on_event_error)

    async def initialize(self):
        await self.bot.wait_until_ready()
    
    def get_log_channel(self):
        return self.bot.get_guild(GuildSupport.SERVER_ID).get_channel(GuildSupport.LOG_FILE_CHANNEL_ID)    

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    @commands.is_owner()
    @commands.command(pass_context=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.is_owner()
    @commands.command(pass_context=True, name='log')
    async def log(self, ctx):
        """ Generates the log file of the bot for bebugging"""
        log_channel = self.get_log_channel()
        directory=os.getcwd()
        logging.info(f"-----------------------------------log backup generated------------------------------")
        file = discord.File(os.path.join(directory+BotFiles.LOG_FILE_LOC),filename=BotFiles.LOG_FILE_NAME)
        await log_channel.send(file=file)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)
    @commands.is_owner()
    @commands.command(pass_context=True, name='backup')
    async def backup(self, ctx):
        """ Generates the log file of the bot for bebugging"""
        directory=os.path.join(os.getcwd()+BotFiles.ATTACK_TABLE_LOC)
        await self.db.backup_attack_table(str(directory))
        log_channel = self.get_log_channel()
        file = discord.File(directory,filename=BotFiles.ATTACK_TABLE_NAME)
        await log_channel.send(file=file)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)
    
    '''@commands.command(pass_context=True, name='t')
    async def test(self, ctx):
        """ Generates the log file of the bot for bebugging"""
        war = await self.bot.coc.get_current_war("#29L9RVCL8")
        attac_table=dict({'war_id':6})
        attack_table=WarAction.attack_updates(war,war.attacks[0],attac_table)
        await self.db.insert_into_attack_table(attack_table)
        content, embed = PrepMessage().prepare_on_war_attack_message(war.attacks[0],war,attack_table)
        await ctx.send(content=content,embed=embed)
        
        await ctx.message.add_reaction(Emoji.GREEN_TICK)'''
    
def setup(bot):
    bot.add_cog(Owner(bot))