import coc
import logging
import asyncio
import gspread
from discord.ext import commands
from application.constants.guild1947 import Guild1947Clan
from application.constants.emoji import Emoji
from application.constants.bot_const import BotImage, BotVariables, BotEmoji
from application.statics.create_message import CreateMessage
from application.database.db_utlis import DbUtlis

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

    def insert_into_google_sheet(self,sheet,insert_row,memberObj,player):
        try:
            find_result = sheet.find(player.tag)
            if int(sheet.cell(find_result.row,1).value) != memberObj.id :
                return True, sheet.row_values(find_result.row)
        except gspread.CellNotFound:
            pass
            
        data = sheet.get_all_records()
        found = False
        pos = 2
        position_row = len(data)+2
        for row in data:
            if str(row.get("discord_id"))== str(memberObj.id):
                found = row
                position_row = pos
            pos +=1
        if found is False:
            sheet.insert_row(insert_row,position_row)
            return True , insert_row
        else:
            if player.tag in found.values():
                return True,found
            else:
                position_coloumn=1
                for k,v in found.items():
                    if v == "":
                        found[k]=player.tag
                        sheet.update_cell(position_row,position_coloumn, player.tag)
                        return True , found
                    position_coloumn +=1
                return False, found

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
            '''
            insert_row = [str(memberObj.id),player.tag]
            result,row = self.insert_into_google_sheet(sheet,insert_row,memberObj,player)
            content=str(result)+str(row) 
            if result:
                if isinstance(row,dict):
                    list_of_tag = list(row.values())
                    if int(row['discord_id'])==memberObj.id:
                        content=f"` {player.name} - ({player.tag})  TH {player.town_hall} ` **is claimed by** {memberObj.mention}   Other linked villages are {list_of_tag[1:]} "
                else:
                    if int(row[0])==memberObj.id :
                        content=f"` {player.name} - ({player.tag})  TH {player.town_hall} ` **is claimed by** {memberObj.mention}   "
                    else:
                        try:
                            memberObj=self.bot.get_guild(ctx.guild.id).get_member(int(row[0]))
                            content=f"` {player.name} - ({player.tag})  TH {player.town_hall} ` **is claimed by** ` {memberObj.display_name} `   "
                        except:
                            #claim member not in guild
                            content=f"{player.name} **is claimed by** user not on this server"
            else:
                list_of_tag = list(row.values())
                content=f"Sorry, You can claim maximum of 5 villages only.  Other linked villages are {list_of_tag[1:]}"'''

            await ctx.send(content=player)
            # except Exception as Ex:
            #     await ctx.send(f" Player not found with player_tag : {player_tag} \n ```{Ex}```")
def setup(bot):
    bot.add_cog(Users(bot))
