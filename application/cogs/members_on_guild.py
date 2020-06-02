import coc 
import discord
from discord.ext import commands
from application.constants.emoji import Emoji
from application.database.db_utlis import DbUtlis
from application.constants.guildsupport import GuildSupport
import logging

class MemberOnGuild(commands.Cog):
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

    @commands.Cog.listener()
    async def on_member_join(self,member):
        guild = member.guild
        await self.db.insert_into_member_on_guild_table(guild.id,member.id)
        logging.info(f"INFO: members_on_guild.py - on_member_join({member.id}) executed")
    
    @commands.Cog.listener()
    async def on_member_remove(self,member):
        guild = member.guild
        await self.db.delete_from_member_on_guild_table(guild.id,member.id)
        logging.info(f"INFO: members_on_guild.py - on_member_remove({member.id}) executed")

def setup(bot):
    bot.add_cog(MemberOnGuild(bot))
