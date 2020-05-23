import coc 
import os
import discord
import logging
import asyncio
from discord.ext import commands
from application.constants.emoji import Emoji
from application.database.db_utlis import DbUtlis
from application.constants.bot_const import BotImage,BotEmoji
from application.statics.prepare_message import PrepMessage
class Admin(commands.Cog):
    """You need administration premission to use this command"""
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.initialize())
        self.db = DbUtlis(self.bot.postgre_db)
    def cog_unload(self):
        self.task.cancel()
        self.bot.coc.remove_events(self.on_event_error)

    async def initialize(self):
        await self.bot.wait_until_ready()

    '''@commands.has_permissions(administrator=True)
    @commands.command(aliases=['Setup'])
    async def setup(self, ctx, channel:discord.TextChannel ):
        """@1947 setup #mentionChannel"""
        await ctx.send("Channel")'''

    @commands.max_concurrency(1)
    @commands.has_permissions(administrator=True)
    @commands.group(invoke_without_command=True, name = "Setup",case_insensitive=True)
    async def setup(self, ctx, channel:discord.TextChannel):
        """ Type `@1947 setup #mentionchannel` This will setup #channel as default channel for bot, You will never have to mention bot again in this channel. Type `help setup` to know more setup  """
        await self.db.add_default_channel(ctx.guild.id,channel.id)
        await channel.send(f"{channel.mention} has been setup as default channel for 1947 bot")
        await ctx.message.add_reaction(Emoji.GREEN_TICK)

    async def clan_link_check(self,ctx,clan,msg):
        logging.info(f"admin.py - clan_link_check {clan.description}")
        if clan.description[-3:]=="EKA":
            embed = discord.Embed(description=f"{Emoji.GREEN_TICK} Clan Linking is successful !")
            await msg.edit(embed=embed)
            await self.db.add_new_clan_tag(ctx.guild.id,clan.tag)
            embed = PrepMessage().prepare_clan_link_message(clan)
            content = (f" Please report {GuildSupport.SERVER_INVITE_URL} for the BOT to start posting updates, immediately. **Since the bot is in beta stage**, war logs are not posted for newly added clans immediately.  ")
            await ctx.send(content=content,embed=embed)
            await ctx.message.add_reaction(Emoji.GREEN_TICK)
            return 
        else:
            await asyncio.sleep(60)
            clan_ = await self.bot.coc.get_clan(clan.tag)
            await self.clan_link_check(ctx,clan_,msg)

    @setup.command( name = "Clan",case_insensitive=True)
    async def clan(self, ctx, clantag:str):
        """ Links a clash of clans to your discord server """
        
        content= "Add `EKA` to last of your clan description as shown in the figure"
        file = discord.File(os.path.join(os.getcwd()+BotImage.LINK_CLAN_IMAGE_LOC),filename=BotImage.LINK_CLAN_IMAGE_NAME)
        await ctx.send(content=content,file=file)
        embed = discord.Embed(description=f"{BotEmoji.LOADING} Clan Linking is in Progress. Please wait..")
        msg= await ctx.send(embed=embed)
        try:
            clantag = coc.utils.correct_tag(clantag)
            clan = await self.bot.coc.get_clan(clantag)
            await asyncio.wait_for(self.clan_link_check(ctx,clan,msg), timeout=300)
        except coc.errors.NotFound:
            embed = discord.Embed(description=f"{BotEmoji.WARNING} Clan Linking is Aborted !!")
            await msg.edit(embed=embed)
            await ctx.send(f"Clan with tag {clantag} is NOT FOUND")
            await ctx.message.add_reaction(Emoji.GREEN_CROSS)
        except asyncio.TimeoutError:
            embed = discord.Embed(description=f"{BotEmoji.WARNING} Clan Linking is Aborted !!")
            await msg.edit(embed=embed)
            await ctx.send(f" Waited too long. Try again after few minutes. It takes 10 mins for COC to update")

    @setup.command( name = "warlog",case_insensitive=True)
    async def war_log(self, ctx,clantag:str, channel:discord.TextChannel,):
        """Setup a channel to announce war logs """
        clantag = coc.utils.correct_tag(clantag)
        try:
            clantag = coc.utils.correct_tag(clantag)
            clan = await self.bot.coc.get_clan(clantag)
            result = await self.db.add_war_log_channel(ctx.guild.id,clan.tag,channel.id)
            print(result,type(result))
            if result:
                await channel.send(f"{channel.mention} has been setup as default WarLog Channel for **{clan.name}**")
                await ctx.message.add_reaction(Emoji.GREEN_TICK)
            else:
                await ctx.send(f"Oh Oh ,Clan **{clan.name}**  is not liked to this server. Try `setup clan` First ")
                await ctx.message.add_reaction(Emoji.GREEN_CROSS)
        except coc.errors.NotFound:
            await ctx.send(f"Clan with tag {clantag} is NOT FOUND")
            await ctx.message.add_reaction(Emoji.GREEN_CROSS)
        #await channel.send(f"{channel.mention} has been setup as default channel for WarLog")

def setup(bot):
    bot.add_cog(Admin(bot))
