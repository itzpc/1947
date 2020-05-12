from discord.ext import commands
from application.constants.guild1947 import Guild1947,Guild1947Message,Guild1947Clan
from application.constants.emoji import Emoji
from application.statics.prepare_message import PrepMessage


class WarReporter(commands.Cog, name="War Report"):
    def __init__(self, bot):
        self.bot = bot

        self.bot.coc.add_events(
            self.on_war_attack,
            self.on_war_state_change
        )
        self.bot.coc.add_war_update([Guild1947Clan.CLAN_TAG,"#9YV8C9U9","#YP8U8QG9"])

    def cog_unload(self):
        self.bot.coc.remove_events(
            self.on_war_attack,
            self.on_war_state_change
        )
        self.bot.coc.stop_updates("war")

    @property
    def report_channel(self):
        return self.bot.get_channel(Guild1947.EKA_WAR_LOG_CHANNEL_ID)

    async def on_war_attack(self, attack, war):
        print(war.clan_tag)
        content, embed = PrepMessage().prepare_on_war_attack_message(attack,war)
        await self.report_channel.send(content=content,embed=embed)

        if war.clan_tag == Guild1947Clan.CLAN_TAG:
            await self.bot.get_channel(708676514400698379).send(content=content,embed=embed) #Coc Api Server
            await self.bot.get_channel(Guild1947.EKA_1947_WAR_LOG_CHANNEL_ID).send(content=content,embed=embed)
        
        print("War attak Ends \n")
    async def on_war_state_change(self, current_state, war):
        await self.report_channel.send(f"{war.clan.name} just entered {current_state} state!")


def setup(bot):
    bot.add_cog(WarReporter(bot))
