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
from application.constants.guildsupport import GuildSupport
from .utlis.paginator import TextPages

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
    @commands.group(invoke_without_command=True, name = "Setup",case_insensitive=True,aliases=['setup'])
    async def setup(self, ctx, channel:discord.TextChannel=None):
        """--> `@1947 setup`- Initial setting up of bot in your server"""
        if channel:
            await self.db.add_default_channel(ctx.guild.id,channel.id)
            await channel.send(f"{channel.mention} has been setup as default channel for 1947 bot")
        else:
            title = "Setup BOT in your server"
            description = "If you have administration previlage use following commands to setup bot in your server."
            embed = discord.Embed(title=title,description=description,color=discord.Color.dark_magenta ()) 
            embed.add_field(name="@1947 setup #mentionChannel", value=f"set the mentioned channel as default channel for the bot to listen to commands. You will never have to mention bot again in this channel for the bot to respond. If this channel is not set, you will have to mention the bot to execute the commands.",inline=False)
            embed.add_field(name="setup clan #clantag", value=f"Links a clan to your discord server",inline=False)
            embed.add_field(name="setup warlog #clantag #mentionChannel", value=f"Setup a channel mentioned to announce war logs of the clantag given",inline=False)
            embed.add_field(name="setup birthday #mentionChannel", value=f"Setup a channel mentioned to announce birthday wishes",inline=False)
            embed.add_field(name="setup recruitment ", value=f"Setup a recruitment system in your server",inline=False)
            embed.add_field(name="setup roster ", value=f"Setup a roster management system in your server",inline=False)
            embed.add_field(name="setup reaction ", value=f"Setup a reaction management system in your server",inline=False)
            embed.add_field(name="setup log ", value=f"Setup a activity log management system in your server",inline=False)
            content = " Type `help setup <command_name>` to know more"
            await ctx.send(content=content,embed=embed)
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
        """--> `setup clan #clantag` - Links a clan to your discord server """
        
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
        """--> `setup warlog #clantag #mentionChannel` - Setup a channel to announce war logs """
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
        try:
            await channel.send(f"{channel.mention} has been setup as default channel for WarLog")
        except:
            await ctx.send(f"Oops ! It seems like I dont have permission to view {channel.mention}")

    @setup.command( name = "Birthday",case_insensitive=True,aliases=['bday'])
    async def birthday(self, ctx, channel:discord.TextChannel):
        """--> `setup birthday #mentionChannel` - Setup a channel to announce birthday wishes """
        result = await self.db.add_bday_announce_channel(ctx.guild.id,channel.id)
        if result:
            try:
                await channel.send(f"{channel.mention} has been setup as birthday announcement channel")
            except:
                await ctx.send(f"Oh Oh, looks like I dont have access to {channel.mention}")
            await ctx.message.add_reaction(Emoji.GREEN_TICK)
        else:
            await ctx.message.add_reaction(Emoji.GREEN_CROSS)

    @setup.command( name = "Recruitment",case_insensitive=True)
    async def recruitment(self, ctx):
        """--> `setup recruitment` - Setup a recruitment management system in your server """
        ctx.send("This feature will be rolled out in the next release. Stay tight !")
    
    @setup.command( name = "Roster",case_insensitive=True)
    async def roster(self, ctx):
        """--> `setup recruitment` - Setup a roster management system in your server """
        ctx.send("This feature will be rolled out in the next release. Stay tight !")
    
    @setup.command( name = "Reaction",case_insensitive=True)
    async def reaction(self, ctx):
        """--> `setup reaction` - Setup a reaction management system in your server """
        ctx.send("This feature will be rolled out in the next release. Stay tight !")
    
    @setup.command( name = "Log",case_insensitive=True)
    async def log(self, ctx):
        """--> `setup reaction` - Setup a activity log update system in your server """
        ctx.send("This feature will be rolled out in the next release. Stay tight !")
    

    @commands.has_permissions(administrator=True)
    @commands.command(name="Announce",case_insensitive=True,aliases=["announce","announcement","Announcement"])
    async def announcement(self,ctx,channel:discord.TextChannel,*,message:str):
        """--> `Announce #mentionChannel message` - BOT sends out a message to a channel"""
        if message:
            embed =PrepMessage().prepare_user_message_embed(ctx.message.author,message,"Announcement")
            await channel.send(embed=embed)
        else:
            await ctx.send("You have not specified the message")
        await ctx.message.add_reaction(Emoji.GREEN_TICK)
    
    @commands.has_permissions(manage_roles=True)
    @commands.group(invoke_without_command=True, name = "Role",case_insensitive=True,aliases=["role"])
    async def role_management(self, ctx):
        """--> `help role` Role Management commands """
        title = "Role Management"
        description = "We support few role management commands. You need to have role management permission to execute them"
        embed = discord.Embed(title=title,description=description,color=discord.Color.dark_magenta ()) 
        embed.add_field(name="Role add @mentionUser rolename", value=f"add a role to user mentioned",inline=False)
        embed.add_field(name="Role remove @mentionUser rolename", value=f"removes a role from user mentioned",inline=False)
        content = " Type `help role <command_name>` to know more"
        await ctx.send(content=content,embed=embed)
    
    @role_management.command( name = "add",case_insensitive=True)
    async def add_role(self, ctx, member:discord.Member,*,role:str):
        """--> `Role add @mentionUser RoleName` - Add a Role with Role Name to user"""
        if ctx.guild.id == GuildSupport.SERVER_ID_1947:
                msg = f" Sorry, This command is disabled in 1947 server due to security reasons !"
                ctx.send(msg)
                ctx.message.add_reaction(Emoji.GREEN_TICK)
        else:
            try:
                GuildObj= self.bot.get_guild(ctx.guild.id)
                print(role,role.strip) 
                roleObj = discord.utils.get(GuildObj.roles, name = role.strip())
                if roleObj in member.roles:
                    msg = f"{member.display_name} already has `{role}` role."
                    await ctx.send(msg)
                else:
                    msg = f"{member.display_name} have been given `{role}` role."
                    await member.add_roles(roleObj)
                    await ctx.send(msg)
                await ctx.message.add_reaction(Emoji.GREEN_TICK)
            except Exception as Ex:
                msg = f"Could not find a role named `{role}` or 1947 BOT is having a lower role than the one requested to assign to user"
                await ctx.send(msg)
                await ctx.message.add_reaction(Emoji.GREEN_TICK)
                logging.error(f"admin.py - add_role({member.id},{role}) - GuildID({ctx.guild.id}) - Exception {Ex}")
    @role_management.command( name = "remove",case_insensitive=True)
    async def remove_role(self, ctx, member:discord.Member,*,role:str):
        """--> `Role remove @mentionUser RoleName` - Removes a Role with Role Name to user"""
        if ctx.guild.id == GuildSupport.SERVER_ID_1947:
                msg = f" Sorry, This command is disabled in 1947 server due to security reasons !"
                ctx.send(msg)
                ctx.message.add_reaction(Emoji.GREEN_TICK)
        else:
            try:
                GuildObj= self.bot.get_guild(ctx.guild.id)
                roleObj = discord.utils.get(GuildObj.roles, name = role.strip())
                if roleObj not in member.roles:
                    msg = f"{member.display_name} do not have `{role}` role. - Remove role operation aborted !"
                    await ctx.send(msg)
                else:
                    
                    msg = f"{member.display_name} have been removed `{role}` role."
                    await member.remove_roles(roleObj)
                    await ctx.send(msg)
                await ctx.message.add_reaction(Emoji.GREEN_TICK)
            except Exception as Ex:
                msg = f"Could not find a role named `{role}` \n or 1947 BOT is having a lower role than the one requested to assign to user\n or there could be multiple roles with the same name, \nTry mentioning a role"
                await ctx.send(msg)
                await ctx.message.add_reaction(Emoji.GREEN_TICK)
                logging.error(f"admin.py - add_role({member.id},{role}) - GuildID({ctx.guild.id}) - Exception {Ex}")
    @commands.has_permissions(administrator=True)
    @commands.command(name="Kick",case_insensitive=True,aliases=["kick"])
    async def kick(self,ctx,member:discord.Member,*,message:str):
        """--> `Kick @mentionMember <optionalreason>` - Kick a member from server"""
        if member:
            await member.kick(reason=message)
            msg = f"{member.display_name} has been kicked out . Reason - {message} "
            await ctx.send(msg)
        await ctx.message.add_reaction(Emoji.GREEN_TICK)
    
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['Ban'])
    async def ban(self,ctx,user:discord.Member,*,message:str=None):
        """--> `Ban @mentionMember <optionalreason>` - Bans a member from server"""
        if user:
            await user.ban(reason=message)
            msg = f"{user.display_name} has been banned from server . Reason - {message} "
            await ctx.send(msg)
            ban_entry=await ctx.guild.bans()
            if ban_entry:
                text = f" **List of Banned  Members in {ctx.guild} server**\n"
                count =1
                for entry in ban_entry:
                    text += f"{count}. {entry.user.name} - {entry.user.id} - {entry.reason}"
                p = TextPages(ctx, text=text ,max_size=500)
                await p.paginate()

        await ctx.message.add_reaction(Emoji.GREEN_TICK)
    
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['Unban'])
    async def unban(self,ctx,user_id:int=None):
        """--> `Unban userID ` - Unban a member from server with user id """
        if user_id:

            try:
                userObj =  self.bot.get_user(user_id)
                await ctx.guild.unban(userObj)
                await ctx.send(f"{userObj.name} has been unbanned from {ctx.guild}.")
            except:
                await ctx.send(f"user with id {user_id} is not exists.")    
        else:
            ban_entry=await ctx.guild.bans()
            if ban_entry:
                text = f" **List of Banned  Members in {ctx.guild} server**\n"
                count =1
                for entry in ban_entry:
                    text += f"{count}. {entry.user.name} - {entry.user.id} - {entry.reason}"
                p = TextPages(ctx, text=text ,max_size=500)
                await p.paginate()
            await ctx.send(f"`unban user_id` - please check the user id from the list of unbanned members.")

        await ctx.message.add_reaction(Emoji.GREEN_TICK)

def setup(bot):
    bot.add_cog(Admin(bot))
