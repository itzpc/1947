import logging
from discord.ext import commands
from discord.ext import tasks
from application.constants.guild1947 import Guild1947,Guild1947Message,Guild1947Clan
from application.constants.emoji import Emoji
from application.statics.prepare_message import PrepMessage
from application.database.db_utlis import DbUtlis

class WarReporter(commands.Cog, name="War Report"):
    def __init__(self, bot):
        self.bot = bot

        self.bot.coc.add_events(
            self.on_war_attack,
            self.on_war_state_change
        )
        self.db = DbUtlis(self.bot.postgre_db)
        self.task = self.bot.loop.create_task(self.initialize())
        #clan_list=["#9YV8C9U9","#LY2UJ02C","#VJQVU98U","#8V8UU9V","#902PQVRL","#2Y09LV28"]
        #self.bot.coc.add_war_update(clan_list)

    def cog_unload(self):
        self.bot.coc.remove_events(
            self.on_war_attack,
            self.on_war_state_change
        )
        self.bot.coc.stop_updates("war")
        #self.periodic_check.stop()
        self.task.cancel()
    
    async def initialize(self):
        await self.bot.wait_until_ready()
        #self.periodic_check.start()
        clan_list = await self.db.get_list_of_public_clan_tags()
        self.bot.coc.add_war_update(clan_list)
    '''
    @tasks.loop(minutes=10)
    async def periodic_check(self):
        try:
            logging.info("Enters periodic_check")
            #clan_list = await self.db.get_list_of_public_clan_tags()
            clan_list=["#9YV8C9U9","#LY2UJ02C","#VJQVU98U","#8V8UU9V","#902PQVRL","#2Y09LV28","#G88CYQP","#8J8QJ2LV","#UPVV99V","#P9UUJLV","#20CCR22U","#8JL9QP8Y","#8YYRVUYC","#2JU0P82U","#YPCCUR8"]
            self.bot.coc.add_war_update(clan_list)
            logging.info("left periodic_check")
        except Exception as Ex:
            print(Ex)
            logging.error("ERROR in on_loop.py : periodic_check () : {}".format(traceback.format_exc()))
    '''
    async def send_war_report(self,clantag,content,embed):

        dict_of_reporting_channels = await self.db.get_dict_of_guild_war_log_channel_of_clan(clantag)
        if dict_of_reporting_channels:
            for reporting_channels in dict_of_reporting_channels:
                try:
                    guild =  self.bot.get_guild(reporting_channels['guild_id'])
                    channel =  guild.get_channel(reporting_channels['channel_id'])
                    logging.error(f"war_report.py - send_war_report({clantag}) - message send channel{channel.id}")
                    await channel.send(content=content,embed=embed)
                except Exception as Ex:
                    logging.error(f"war_report.py - send_war_report({clantag}) - Exception {Ex}")
        return 

    async def on_war_attack(self, attack, war):
        print(war.clan_tag)
        logging.info(f"war_report.py - on_war_attack({attack},{war})")
        content, embed = PrepMessage().prepare_on_war_attack_message(attack,war)
        await self.send_war_report(war.clan_tag,content,embed)
        await self.report_channel.send(content=content,embed=embed)

    async def on_war_state_change(self, current_state, war):
        print(war.clan_tag)
        logging.info(f"war_report.py - on_war_state_change({current_state},{war})")
        await self.report_channel.send(f"{war.clan.name} just entered {current_state} state!")
        
    @property
    def report_channel(self):
        return self.bot.get_channel(Guild1947.EKA_WAR_LOG_CHANNEL_ID)

def setup(bot):
    bot.add_cog(WarReporter(bot))
