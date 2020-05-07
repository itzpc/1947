from discord.ext import commands
from application.constants.guild1947 import Guild1947,Guild1947Message,Guild1947Clan
from application.constants.emoji import Emoji

class WarReporter(commands.Cog, name="War Report"):
    def __init__(self, bot):
        self.bot = bot

        self.bot.coc.add_events(
            self.on_war_attack,
            self.on_war_state_change
        )
        self.bot.coc.add_war_update(Guild1947Clan.CLAN_TAG)

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
        print("on war attack")
        if attack.attacker.is_opponent:
            verb = f"{Emoji.BACKWARD_RED}"
        else:
            verb = f"{Emoji.FORWARD_GREEN}"
        print(attack.attacker)
        
        await self.report_channel.send(Guild1947Message.REPORT_STYLE.format(att=attack, verb=verb))

    async def on_war_state_change(self, current_state, war):
        print("on war state change")
        await self.report_channel.send("{0.clan.name} just entered {1} state!".format(war, current_state))


def setup(bot):
    bot.add_cog(WarReporter(bot))
