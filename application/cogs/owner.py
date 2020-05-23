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
from application.constants.bot_const import BotImage,BotEmoji
from application.statics.prepare_message import PrepMessage



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
    @commands.command(aliases=['join'])
    async def invite(self, ctx):
        """BOT Joins a server."""
        perms = discord.Permissions.none()
        # perms.administrator = True
        perms.read_messages = True
        perms.external_emojis = True
        perms.send_messages = True
        perms.manage_roles = True
        perms.manage_channels = True
        perms.ban_members = True
        perms.kick_members = True
        perms.manage_messages = True
        perms.embed_links = True
        perms.read_message_history = True
        perms.attach_files = True
        perms.add_reactions = True
        perms.manage_guild = True
        #perms.change_nickname = True
        perms.create_instant_invite = True
        perms.manage_guild = True
        #perms.view_audit_log = True
        perms.stream = True
        perms.manage_webhooks = True
        perms.manage_nicknames = True
        perms.connect = True
        perms.speak = True
        perms.mute_members = True
       # perms.deafen_members = True
       # perms.move_members = True
       # perms.use_voice_activation = True

        await ctx.author.send(f'<{discord.utils.oauth_url(self.bot.user.id, perms)}>')
        await ctx.message.add_reaction(Emoji.GREEN_TICK)


def setup(bot):
    bot.add_cog(Owner(bot))