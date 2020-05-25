import coc
import logging
import asyncio
import gspread
import discord
from discord.ext import commands
from application.constants.guild1947 import Guild1947Clan
from application.constants.emoji import Emoji
from application.constants.bot_const import BotImage, BotVariables, BotEmoji
from application.statics.create_message import CreateMessage
from application.database.db_utlis import DbUtlis
from datetime import datetime,date
from .utlis.paginator import TextPages
from .utlis.birthday import Birthday

class Users(commands.Cog):
    """Everyone can use this commands"""
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.initialize())
        self.db = DbUtlis(self.bot.postgre_db)
    def cog_unload(self):
        self.task.cancel()
        self.bot.coc.remove_events(self.on_event_error)

    async def initialize(self):
        await self.bot.wait_until_ready()

    @staticmethod
    def get_list_of_war_log_channel_from_list_of_record(records):
        war_log_dict_list=list()
        for record in records:
            war_log_dict_list.append({'clantag':record['clan_tag'],'warlog':record['war_log_channel']})
        return war_log_dict_list

    @staticmethod
    def get_clan_tag_in_current_channel(current_channel,list_of_channel_dic):
        logging.info(f"users.py - get_clan_tag_in_current_channel({current_channel},{list_of_channel_dic})")
        clan_tag = None
        if list_of_channel_dic:
            for record in list_of_channel_dic:
                if current_channel in record.values():
                    clan_tag = record['clantag']
                    return clan_tag
        return clan_tag

    @commands.command(name="Clan", aliases=["c","C","clan"])
    async def search_clan(self, ctx, clan_tag):
        """Search a clan by clan tag"""
        try:
            
            clan_tag = coc.utils.correct_tag(clan_tag)
            clan = await self.bot.coc.get_clan(clan_tag)
            content = f"The clan name for {clan_tag} is {clan.name}.\n"
            content += f"{clan.name} currently has {clan.member_count} members.\n\n"

            war = await self.bot.coc.get_current_war(clan_tag)
            if war:
                content += f"Current war state is {war.state}\n"
                if war.state != "notInWar":
                    content += f"Opponent: {war.opponent}"

            await ctx.send(content)
            await ctx.message.add_reaction(Emoji.GREEN_TICK)
        except Exception as Ex:
            await ctx.message.add_reaction(Emoji.GREEN_CROSS)
            logging.error(f"clan_search {Ex} ")

    @commands.max_concurrency(1)
    @commands.command(name="Stats", aliases=["warstatus","Status","stats","status"],case_insensitive=True)
    async def war_status(self, ctx):
        "Get the current war status of your clan"
        clan_tag = None
        result= await self.db.get_clans_on_guild_information(ctx.guild.id)
        if result:
            list_channels = self.get_list_of_war_log_channel_from_list_of_record(result)
            clan_tag = self.get_clan_tag_in_current_channel(ctx.channel.id,list_channels)
            if clan_tag is None:
                clan_tag = await self.db.get_default_clan_of_guild(ctx.guild.id)
        else:
            clan_tag = await self.db.get_default_clan_of_guild(ctx.guild.id)

        if clan_tag:
            clan_tag = coc.utils.correct_tag(clan_tag)
            war = await self.bot.coc.get_current_war(clan_tag)
            if war:
                clan_name = war.clan.name
                opponent_name = war.opponent.name
                content = f"`{clan_name}` VS `{opponent_name}`\n Current war state is {war.state}\n"
                content += f"{war.clan.stars}/{war.clan.max_stars} VS {war.opponent.stars}/{war.opponent.max_stars} "
            else:
                content = " No wars found !"
        else:
            content="No Default Clans linked. Try `help setup clan` First"
            
        await ctx.send(content)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)
    
    def prepare_player_found_message(self,player):

        args = dict()
        args["embed_title"]=player.name
        args["author_name"]=player.tag 
        args["embed_title_url"]=player.share_link

        msg=f"**PROFILE**\n\n"
        msg+=f"{Emoji.CLAN} : {player.clan} -\t{player.role} \n⭐ : {player.war_stars} \t 🏆 :({player.trophies}){player.best_trophies} \t "
        msg+=f"\n\n**HERO**\n\n"
        if player.heroes:
            for hero in player.heroes:
                if BotEmoji.heroes_emoji.get(hero.name):
                    msg+=f"{BotEmoji.heroes_emoji[hero.name]}  {hero.level} "
        msg += f"\n\n**VILLAGE BASE TROOPS** \n\n"
        count=0
        for troop_name, troop in player.get_ordered_troops(coc.HOME_TROOP_ORDER).items():
            if count ==7:
                count =0
                msg+=f"\n"
            if BotEmoji.troop_emoji[troop_name]:
                count +=1
                msg+=f"{BotEmoji.troop_emoji[troop_name]}  {troop.level} \t"
        args["embed_description"]=f"  \n{msg}\n"
        if player.town_hall == 13:
            args["set_thumbnail_url"]=BotImage.TH13
        elif player.town_hall == 12:
            args["set_thumbnail_url"]=BotImage.TH12
        elif player.town_hall == 11:
            args["set_thumbnail_url"]=BotImage.TH11
        elif player.town_hall == 10:
            args["set_thumbnail_url"]=BotImage.TH10
        else:
            args["set_thumbnail_url"]=BotImage.TH9

        message=CreateMessage(None,True)
        return message.create_message(**args)

    @commands.max_concurrency(1)
    @commands.command(name="Player", aliases=["P","player","p"],case_insensitive=True)
    async def search_player(self, ctx, player_tag):
        """ Search a Clash of Clans Player by Player ID """
        if player_tag is None :
            await ctx.send(" ` 1947 link #playertag ` - You are missing a player tag to link")
        else:
            try:
                memberObj=self.bot.get_guild(ctx.guild.id).get_member(ctx.author.id)
                player_tag = coc.utils.correct_tag(player_tag)
                player = await self.bot.coc.get_player(player_tag)
                content,embed = self.prepare_player_found_message(player)
                content=f"{player.tag} - Details Found"
                await ctx.send(content=content,embed=embed)
            except Exception as Ex:
                await ctx.send(f" Player not found with player_tag : {player_tag} \n ```{Ex}```")

    @commands.command(aliases=['join'])
    async def invite(self, ctx):
        """BOT Joins a server."""
        if ctx.guild.id == GuildSupport.SERVER_ID:
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
            try:
                await ctx.author.send(f'<{discord.utils.oauth_url(self.bot.user.id, perms)}>')
            except:
                await ctx.send(" Need to enable DM to get the invite link")
            finally:
                await ctx.message.add_reaction(Emoji.GREEN_TICK)
        else:
            ctx.send(f"You need to join support server first to invite bot. {GuildSupport.SERVER_INVITE_URL}")

    @commands.max_concurrency(1)
    @commands.command(name="Claim", aliases=["claim","Cv","cv","Claim_village"])
    async def claim_village(self, ctx, player_tag):
        """ Link a Clash of Clan profile to Discord ID """
        if player_tag is None :
            await ctx.send(" ` 1947 claim #playertag ` - You are missing a player tag to claim village")
        else:
            memberObj=self.bot.get_guild(ctx.guild.id).get_member(ctx.author.id)
            player_tag = coc.utils.correct_tag(player_tag)
            #try:
            player = await self.bot.coc.get_player(player_tag)

            await ctx.send(content=player)
            # except Exception as Ex:
            #     await ctx.send(f" Player not found with player_tag : {player_tag} \n ```{Ex}```")
    @commands.group(invoke_without_command=True, name = "Birthday",case_insensitive=True,aliases=['birthday','bday','Bday'])
    async def birthday(self, ctx):
        """ Birthday commands - help birthday """
        title = "Birthday"
        description = "Celebrate your birthday with friends using the following commands"
        embed = discord.Embed(title=title,description=description,color=discord.Color.dark_magenta ()) 
        embed.add_field(name="birthday add DD-MM-YYYY", value=f"Adds your birthday", inline= False)
        embed.add_field(name="birthday list", value=f"list out registered birthdays", inline= False)
        content = " Type `help birthday` to know more"
        await ctx.send(content=content,embed=embed)

    @birthday.command( name = "add",case_insensitive=True)
    async def add_birthday(self, ctx, message:str):
        """--> `birthday add DD-MM-YYYY` - Add your Birthday to your Discord Profile """
        try:

            if message is None:
                await ctx.send("Oh ! You forget to give me a date in DD-MM-YYYY format")
                return
            msg = message.strip()
            dob = datetime.strptime(msg, "%d-%m-%Y")
            today = date.today()
            guild_id_list = self.bot.guilds 
            member_on_guild_id_list = list()
            for guild in guild_id_list:
                guildObj = self.bot.get_guild(guild.id)
                if guildObj:
                    member=guildObj.get_member(ctx.message.author.id)
                    if member:
                        member_on_guild_id_list.append(guild.id)
            
            result = await self.db.update_birthday(ctx.guild.id,ctx.message.author.id,dob,member_on_guild_id_list)

            if result is True:
                await ctx.message.add_reaction(Emoji.GREEN_TICK)
                if (dob.month == today.month) and (dob.day == today.day):
                    channel_id = await self.db.get_birthday_announce_channel(ctx.guild.id)
                    if channel_id:
                        try:
                            channel = self.bot.get_guild(ctx.guild.id).get_channel(channel_id)
                            await Birthday(channel,ctx.message.author).wish_birthday()
                        except Exception as Ex:
                            await ctx.send(Ex)
    
                            await ctx.send(f"Birthday announce channel not setup. Ask server admin to setup one.")
                            msg= await ctx.send(f"{ctx.message.author.mention} Happy Birthday ")
                            await msg.add_reaction(Emoji.BIRTHDAY)
            else:
                await ctx.message.add_reaction(Emoji.X)

        except Exception as ex:
            await ctx.send(f"Oh ! Provide date in DD-MM-YYYY format only \n {ex}")
        
    
    @birthday.command( name = "list",case_insensitive=True)
    async def list_birthday(self, ctx):
        """--> `birthday list` -  List out the birthdays of server members"""
        
        try:
            result=await self.db.get_member_birthday_list_on_guild(ctx.guild.id)
            text = str()
            today = date.today()
            count=1
            for record in result:
                try:
                    userObj=self.bot.get_user(record['member_id'])
                    if userObj:
                        if (record['dob'].month == today.month) and (record['dob'].day == today.day):
                            text += f"{count}. {Emoji.BIRTHDAY} {userObj.display_name} - {record['dob']} \n "
                        else:
                            text += f"{count}. {userObj.display_name} - {record['dob']} \n"
                        count+=1
                except Exception as Ex:
                    logging.info("users.py : list_bday : Exception {Ex}")
            if text:
                p = TextPages(ctx, text=text ,max_size=500)
                await p.paginate()
            else:
                await ctx.send("No birthdays added `birthday add` to add birthday")
            await ctx.message.add_reaction(Emoji.GREEN_TICK)
        except Exception as Ex:
            logging.error("ERROR : users.py : list_bday :".format(Ex))
        

def setup(bot):
    bot.add_cog(Users(bot))
