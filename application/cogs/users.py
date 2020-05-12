import coc
import logging
import asyncio
import gspread
from discord.ext import commands
from application.utlis.drive_utlis import Drive_Config
from application.constants.guild1947 import Guild1947Clan
from application.constants.emoji import Emoji
from application.constants.bot_const import BotImage, BotVariables, BotEmoji
from application.statics.create_message import CreateMessage
class General(commands.Cog):
    """Description of what this file does"""
    def __init__(self, bot):
        self.bot = bot
        self.drive_client = self.bot.drive.create_client()

    @commands.max_concurrency(1)
    @commands.command(name="search_clan", aliases=["Search_clan","Searchclan","sc","Sc"])
    async def search_clan(self, ctx, clan_tag):
        """Gets clan information from API and displays it for user"""
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
    @commands.command(name="war_status", aliases=["warstatus","status","Status","Stats","stats"])
    async def war_status(self, ctx, clan_tag=None):
        if clan_tag is None:
            clan_tag = Guild1947Clan.CLAN_TAG
        clan_tag = coc.utils.correct_tag(clan_tag)
        war = await self.bot.coc.get_current_war(clan_tag)
        if war:
            clan_name = war.clan.name
            opponent_name = war.opponent.name
            content = f"`{clan_name}` VS `{opponent_name}`\n Current war state is {war.state}\n"
            content += f"{war.clan.stars}/{war.clan.max_stars} VS {war.opponent.stars}/{war.opponent.max_stars} "
        else:
            content = " No wars found !"
        
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
    @commands.command(name="search_player", aliases=["Search","search","Sp","sp","Search_player"])
    async def search_player(self, ctx, player_tag):
        """ 1947 link #playertag """
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
    @commands.command(name="claim_player", aliases=["Claim","claim","Cv","cv","Claim_village"])
    async def claim_village(self, ctx, player_tag):
        """ 1947 claim #playertag """
        if player_tag is None :
            await ctx.send(" ` 1947 claim #playertag ` - You are missing a player tag to claim village")
        else:
            memberObj=self.bot.get_guild(ctx.guild.id).get_member(ctx.author.id)
            player_tag = coc.utils.correct_tag(player_tag)
            #try:
            player = await self.bot.coc.get_player(player_tag)
            drive = Drive_Config()
            drive_client = drive.create_client()
            sheet= drive.open_sheet(drive_client,1)
            data = sheet.get_all_records()
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
                content=f"Sorry, You can claim maximum of 5 villages only.  Other linked villages are {list_of_tag[1:]}"

            await ctx.send(content=content)
            # except Exception as Ex:
            #     await ctx.send(f" Player not found with player_tag : {player_tag} \n ```{Ex}```")
def setup(bot):
    bot.add_cog(General(bot))
