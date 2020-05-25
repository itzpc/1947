import coc
import logging
import asyncio
import gspread
import discord
from discord.ext import commands
from application.constants.guildsupport import GuildSupport
from application.constants.emoji import Emoji
from application.constants.bot_const import BotImage, BotVariables, BotEmoji
from application.statics.create_message import CreateMessage
from application.statics.prepare_message import PrepMessage
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

    @commands.command(aliases=['Av','av','avatar','Avatar'])
    async def user_avatar(self, ctx, user:discord.User):
        """--> `av @mentionUser ` - To view the avatar of a user"""
        if user.bot:
            return
        embed = discord.Embed(title = f"Avatar Requested of EKA Warrior : {user.name}",
            color = 0x98FB98
            )
        embed.set_image(url = user.avatar_url) 
        await ctx.send(embed=embed)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)

    @commands.command(aliases=['Dm','dm','DM'])
    async def dm_user(self, ctx, user:discord.User,msg:str):
        """--> `dm @mentionUser message` - BOT DM's mentioned user a message"""
        if user.bot:
            return
        embed = discord.Embed(title = f"You have a message from : {ctx.message.author}",
            description = msg,
            color = 0x98FB98
            )
        embed.set_thumbnail(url=str(ctx.message.author.avatar_url))
        
        try:
            await user.send(embed=embed)
            Msg=await ctx.send(f"Hey {ctx.message.author}, Your secret message has been sent to the user.")
            await Msg.add_reaction(Emoji.GREEN_TICK)
        except:
            Msg=await ctx.send(f"Sorry {ctx.message.author}, The user has disabled DM. Your secret message could not be sent.")
            await Msg.add_reaction(Emoji.X)
        await ctx.message.delete()
    
    @commands.command(aliases=['Profile'])
    async def profile(self, ctx):
        """--> profile - Display the user's profile"""
        member_info = await self.db.get_member_info_on_guild(ctx.guild.id,ctx.message.author.id)
        embed =  PrepMessage().prepare_profile_message(member_info,ctx.message.author)
        await ctx.send(embed=embed)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)
    
    @commands.command(aliases=['Whois'])
    async def whois(self, ctx,user:discord.Member):
        """--> profile - Display the user's profile"""
        member_info = await self.db.get_member_info_on_guild(ctx.guild.id,user.id)
        embed =  PrepMessage().prepare_profile_message(member_info,user)
        await ctx.send(embed=embed)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)

    @commands.command(aliases=['join'])
    async def invite(self, ctx):
        """--> `invite` - Invite BOT link to add to your server."""
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

    @commands.group(invoke_without_command=True, name = "Birthday",case_insensitive=True,aliases=['birthday','bday','Bday'])
    async def birthday(self, ctx):
        """--> `birthday` - Various Birthday commands, `help birthday` to explore more """
        title = "Birthday"
        description = "Celebrate your birthday with friends using the following commands"
        embed = discord.Embed(title=title,description=description,color=discord.Color.dark_magenta ()) 
        embed.add_field(name="birthday add DD-MM-YYYY", value=f"Adds your birthday", inline= False)
        embed.add_field(name="birthday list", value=f"list out registered birthdays", inline= False)
        content = " Type `help birthday <command>` to know more about each birthday commands"
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
                            text += f"{count}. {Emoji.BIRTHDAY} {userObj.display_name} - {record['dob']} \n"
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
        
    @commands.group(invoke_without_command=True, name = "report",case_insensitive=True,aliases=['Report'])
    async def report(self, ctx):
        """--> `report` - Report activity to 1947 BOT Admin """
        title = "Report"
        description = "Report following actions to 1947 BOT Developers"
        embed = discord.Embed(title=title,description=description,color=discord.Color.dark_magenta()) 
        embed.add_field(name="report bug", value=f"To report any bug", inline= False)
        embed.add_field(name="report feature", value=f"To report any new feature you want to see in the next release", inline= False)
        embed.add_field(name="report suggest", value=f"To suggest any improvements to existing feature you want to see in the next release", inline= False)
        content = " Type `help report <command>` to know more about each commands"
        await ctx.send(content=content,embed=embed)

    @report.command( name = "bug",case_insensitive=True)
    async def report_bug(self, ctx,* ,body:str):
        """--> `report bug <explain bug> - To report a bug"""
        body=body[:1500]
        embed = discord.Embed(title="BUG",description=f"`{ctx.message.author.id}` reported a bug in `{ctx.guild.id}` \n```{body}```",color=discord.Color.red())
        embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await self.bot.get_guild(GuildSupport.SERVER_ID).get_channel(GuildSupport.REPORT_CHANNEL_ID).send(embed=embed)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)

    @report.command( name = "feature",case_insensitive=True)
    async def report_feature(self, ctx,* ,body:str):
        """--> `report feature <explain feature> - To report a new feature you want to see it on BOT"""
        body=body[:1500]
        embed = discord.Embed(title="NEW FEATURE REQUEST",description=f"`{ctx.message.author.id}` reported a new feature in `{ctx.guild.id}` \n```{body}```",color=discord.Color.green())
        embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await self.bot.get_guild(GuildSupport.SERVER_ID).get_channel(GuildSupport.REPORT_CHANNEL_ID).send(embed=embed)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)

    @report.command( name = "suggest",case_insensitive=True)
    async def report_suggest(self, ctx,* ,body:str):
        """--> `report suggest <explain suggestions> - To report a suggestion on existing feature of 1947 BOT"""
        body=body[:1500]
        embed = discord.Embed(title="SUGGEST CHANGE IN FEATURE ",description=f"`{ctx.message.author.id}` reported a suggestion about a feature in `{ctx.guild.id}` \n```{body}```",color=discord.Color.blue())
        embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await self.bot.get_guild(GuildSupport.SERVER_ID).get_channel(GuildSupport.REPORT_CHANNEL_ID).send(embed=embed)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)

def setup(bot):
    bot.add_cog(Users(bot))
