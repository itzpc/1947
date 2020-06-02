import logging
from discord.ext import commands
from discord.ext import tasks
from application.constants.guild1947 import Guild1947,Guild1947Message,Guild1947Clan
from application.constants.emoji import Emoji
from application.statics.prepare_message import PrepMessage
from application.statics.war_action import WarAction
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
        logging.info(f"war_report.py - on_war_attack({attack},{war})")
        home_clan= war.clan_tag
        opponentclan =war.opponent.tag
        war_id = await self.db.get_war_id_from_war_table(home_clan,opponentclan)
        if war_id:
            attack_table ={'war_id':war_id}
        else:
            war_table_insert=WarAction.war_state_prep_updates(war)
            await self.db.insert_into_war_table(war_table_insert)
            war_id = await self.db.get_war_id_from_war_table(home_clan,opponentclan)
            attack_table = {'war_id':war_id}
        
        attack_table=WarAction.attack_updates(war,attack,attack_table)
        await self.db.insert_into_attack_table(attack_table)
        content, embed = PrepMessage().prepare_on_war_attack_message(attack,war,attack_table)
        await self.send_war_report(war.clan_tag,content,embed)
        await self.report_channel.send(content=content,embed=embed)
        logging.info(f"INFO - war_report.py on_war_attack() executed - for clan tag {war.clan_tag}")

    async def on_war_state_change(self, current_state, war):
        logging.info(f"war_report.py - on_war_state_change({current_state},{war})")
        if current_state == "preparation":
            war_table_insert=WarAction.war_state_prep_updates(war)
            await self.db.insert_into_war_table(war_table_insert)
        elif current_state == "warEnded":
            war_table_insert=WarAction.war_state_end_updates(war)
            await self.db.update_war_table(war_table_insert)
        await self.state_channel.send(f"{war.clan.name} just entered {current_state} state!")
        logging.info(f"INFO - war_report.py on_war_state_change() executed - for clan tag {war.clan_tag}")
        
    @property
    def report_channel(self):
        return self.bot.get_channel(Guild1947.EKA_WAR_LOG_CHANNEL_ID)
    @property
    def state_channel(self):
        return self.bot.get_channel(Guild1947.GLOBAL_STATE_CHANGE_CHANNEL_ID)

def setup(bot):
    bot.add_cog(WarReporter(bot))
