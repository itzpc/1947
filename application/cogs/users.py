import coc
import logging
from discord.ext import commands
from application.constants.guild1947 import Guild1947Clan
from application.constants.emoji import Emoji
class General(commands.Cog):
    """Description of what this file does"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clan_search", aliases=["clansearch"])
    async def clan_search(self, ctx, clan_tag):
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

    @commands.command(name="war_status", aliases=["warstatus","status"])
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

def setup(bot):
    bot.add_cog(General(bot))