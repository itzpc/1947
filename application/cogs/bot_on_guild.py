import coc 
import discord
from discord.ext import commands
from application.constants.emoji import Emoji
from application.database.db_utlis import DbUtlis

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

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.db.insert_into_bot_table(guild.id)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.db.delete_from_bot_table(guild.id)

def setup(bot):
    bot.add_cog(BotOnGuild(bot))
