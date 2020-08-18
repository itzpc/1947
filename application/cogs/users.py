import coc
import logging
import asyncio
import gspread
import discord
import aiohttp
from aiohttp import ClientSession
from discord.ext import commands
from application.constants.guildsupport import GuildSupport
from application.constants.emoji import Emoji
from application.constants.bot_const import BotImage, BotVariables, BotEmoji
from application.statics.create_message import CreateMessage
from application.statics.prepare_message import PrepMessage
from application.database.db_utlis import DbUtlis
from datetime import datetime,date,timedelta

from .utlis.paginator import TextPages
from .utlis.birthday import Birthday
from .utlis import ailotime
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
                    logging.info("WARNING: users.py : list_bday : Exception {Ex}")
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

    @commands.group(invoke_without_command=True, name = "Covid",case_insensitive=True,aliases=['covid'])
    async def covid(self, ctx):
        """--> `covid` - Get some information about covid """
        title = "Covid"
        description = "Get some information about covid "
        embed = discord.Embed(title=title,description=description,color=discord.Color.dark_magenta()) 
        embed.add_field(name="covid state <state name>", value=f"To get covid information about the state provided. (India Only)", inline= False)
        
        content = " Type `help covid <command>` to know more about each commands"
        await ctx.send(content=content,embed=embed)

    @commands.max_concurrency(1)
    @covid.command( name = "State",case_insensitive=True)
    async def covid_state(self, ctx,*,state_name:str):
        """--> `covid state <state name> - To get covid information about the state provided.T"""
        data=None
        found = False
        url = 'https://api.covid19india.org/data.json'
        url1 = 'https://api.covid19india.org/states_daily.json'
        async with ClientSession() as session:
            try:
                response = await session.request(method='GET', url=url)
                response1 = await session.request(method='GET', url=url1)
                response.raise_for_status()
                response1.raise_for_status()
            except aiohttp.HTTPError as http_err:
                logging.error(f"ERROR users.py covid_state() - {http_err}")
            except Exception as err:
                logging.error(f"ERROR users.py covid_state() - {err}")
            response_json = await response.json()
            response_json1 = await response1.json()
            data=response_json
            response_json1 = await response1.json()
            data1=response_json1
        if data is None or data1 is None:
            await ctx.send(f" The service is down, Try again later`")
            await ctx.message.add_reaction(Emoji.GREEN_CROSS)
        else:
            daily_data=data1['states_daily']
            state_wise= data['statewise']
            for state in state_wise:
                if state['state'].lower() == state_name.strip().lower():
                    embed = discord.Embed(title="Covid",description=f"Information about {state_name}",color=discord.Color.red())
                    image_url = "https://www.wistv.com/resizer/bd1BCPA4OPS3RW9WN31ji5HZFQk=/1200x0/arc-anglerfish-arc2-prod-raycom.s3.amazonaws.com/public/DAJYEGYUBREQZPVTJ6FRZNFEKA.png"
                    #embed.set_image(url = image_url) 
                    embed.add_field(name="State", value=state['state'], inline= True)
                    embed.add_field(name="Last Updated", value=state['lastupdatedtime'], inline= True)
                    embed.add_field(name="Total Active Cases", value=state['active'], inline= True)
                    embed.add_field(name="Total Confirmed Cases", value=state['confirmed'], inline= True)
                    embed.add_field(name="Total Death", value=state['deaths'], inline= True)
                    embed.add_field(name="Total Recovered Cases", value=state['recovered'], inline= True)
                    today=datetime.utcnow()
                    yesterday = today -timedelta(days = 1) 
                    today = today.strftime("%d-%b-%y")
                    yesterday = yesterday.strftime("%d-%b-%y")
                    state_code=str(state['statecode'].lower())
                    for day in daily_data:
                        if day['date'] == today:
                            if day['status'].strip().lower() == "confirmed":
                                confirmed_today =day.get(state_code,None)
                                if confirmed_today:
                                    embed.add_field(name="Confirmed Today Cases", value=confirmed_today, inline= True)
                            if day['status'].strip().lower() == "recovered":
                                recovered_today =day.get(state_code,None)
                                if recovered_today:
                                    embed.add_field(name="Recovered Today Cases", value=recovered_today, inline= True)
                            if day['status'].strip().lower() == "deceased":
                                deceased_today =day.get(state_code,None)
                                if deceased_today:
                                    embed.add_field(name="Recovered Today Cases", value=deceased_today, inline= True)
                        if day['date'] == yesterday:
                            if day['status'].strip().lower() == "confirmed":
                                confirmed_yesterday =day.get(state_code,None)
                                if confirmed_yesterday:
                                    embed.add_field(name="Confirmed Yesterday Cases", value=confirmed_yesterday, inline= True)
                            if day['status'].strip().lower() == "recovered":
                                recovered_yesterday =day.get(state_code,None)
                                if recovered_yesterday:
                                    embed.add_field(name="Recovered Yesterday Cases", value=recovered_yesterday, inline= True)
                            if day['status'].strip().lower() == "deceased":
                                deceased_yesterday =day.get(state_code,None)
                                if deceased_yesterday:
                                    embed.add_field(name="Recovered Yesterday Cases", value=deceased_yesterday, inline= True)
                    found = True
                    await ctx.send(embed=embed)
                    await ctx.message.add_reaction(Emoji.GREEN_TICK)
            if found == False:
                await ctx.send(f" We dont have information about state : `{state_name}`")
                await ctx.message.add_reaction(Emoji.GREEN_CROSS)

    @commands.command(aliases=['Info'])
    async def info(self, ctx):
        """--> `info` -  Little information about bot"""
        bot_info = await self.db.get_bot_info(BotVariables.BOT_ID)
        title = "BOT is Online"
        description = f"Info"
        last_down_time = bot_info['last_down_time']
        now = datetime.utcnow()
        time_diff = now-last_down_time
        duration = time_diff/60 
        embed = discord.Embed(title=title,description=description,color=discord.Color.green()) 
        embed.add_field(name="Bot Owner", value=f"Pc",inline=False)
        embed.add_field(name="Bot Version", value=f"{self.bot.version}" )
        embed.add_field(name="Last Down time", value=last_down_time, inline=True)
        embed.add_field(name="Last Down Duration", value=f"Lasted {duration.seconds} seconds", inline=True)
        embed.add_field(name="Up Time", value=f"About {time_diff.days} days", inline=True)
        embed.add_field(name="Last Periodic Check", value=bot_info['last_check'], inline=True)
        embed.add_field(name="Discord Version", value=f"{discord.__version__}" )
        embed.add_field(name="COC Version", value=f"{coc.__version__}" )
        embed.add_field(name="# Servers", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="# Users", value=f"{len(self.bot.users)}", inline=True)
        await ctx.send(embed=embed)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)
    @commands.command(aliases=['Conv','conv','Convert'])
    async def convert(self, ctx,*,input:str):
        """--> `conv HH:MM in CountryCode to CountryCode` - conv 13:00 in IN to CA  """
        logging.info("WARNING: convert exe")
        try:
            output = ailotime.command_conv(input)
            embed_answer = discord.Embed(title=output.title, description='\n'.join(output.description), color=int(output.color, 16))
            await ctx.send(embed=embed_answer)
            await ctx.message.add_reaction(Emoji.GREEN_TICK)
        except:
            await ctx.send('Type `conv 13:00 in IN to CA` to convert. Mention Time in 24HR format')
def setup(bot):
    bot.add_cog(Users(bot))
