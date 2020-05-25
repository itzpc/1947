import logging
from discord.ext import commands
from discord.ext import tasks
from application.constants.guild1947 import Guild1947,Guild1947Message,Guild1947Clan
from application.constants.emoji import Emoji
from application.statics.prepare_message import PrepMessage
from application.database.db_utlis import DbUtlis
from application.constants.bot_const import BotVariables
from datetime import datetime,date
from .utlis.birthday import Birthday

class TaskLoop(commands.Cog, name="Loop Tasks"):
    def __init__(self, bot):
        self.bot = bot
        self.db = DbUtlis(self.bot.postgre_db)
        self.task = self.bot.loop.create_task(self.initialize())

    def cog_unload(self):
        self.bot.coc.stop_updates("war")
        self.periodic_check.stop()
        self.task.cancel()
    
    async def initialize(self):
        await self.bot.wait_until_ready()
        self.periodic_check.start()
    @staticmethod
    async def birthday_checker(bot,db):
        logging.info(f"INFO: task_loop.py - birthday_checker() ")
        today = date.today()
        logging.info(f"INFO: task_loop.py - birthday_checker() - getting list_birthday_announce_dict START")
        list_birthday_announce_dict = await db.get_list_birthday_announce_dict()
        logging.info(f"INFO: task_loop.py - birthday_checker() - getting list_birthday_announce_dict END")
        if list_birthday_announce_dict:
            logging.info(f"INFO: task_loop.py - birthday_checker() - Some birthday updates are processing")
            for row in list_birthday_announce_dict:
                if row['birthday_member_list']:
                    wish_channel_id = await db.get_birthday_announce_channel(row['guild_id'])
                    if wish_channel_id:
                        try:
                            wish_channel = bot.get_channel(wish_channel_id)
                            for member_id in row['birthday_member_list']:
                                try:
                                    memberObj = bot.get_guild(row['guild_id']).get_member(member_id)
                                    await Birthday(wish_channel,memberObj).wish_birthday()
                                except Exception as Ex:
                                    logging.error(f"ERROR: task_loop.py -birthday_checker() - Exception {Ex}")
                        except Exception as Ex:
                            logging.error(f"ERROR: task_loop.py -birthday_checker() - Exception {Ex}")

            logging.info(f"INFO: task_loop.py - birthday_checker() - Birthday updates processing complete")
        else:
            logging.info(f"INFO: task_loop.py - birthday_checker() - No birthday updates {list_birthday_announce_dict}")
        await db.update_last_check_in_bot_info(BotVariables.BOT_ID)
    @tasks.loop(hours=10)
    async def periodic_check(self):
        try:
            logging.info("INFO: task_loop - periodic_check - started")
            last_run = await self.db.get_last_run_from_bot_info(BotVariables.BOT_ID)
            now_time = datetime.utcnow()
            time_diiference = now_time - last_run
            if time_diiference.days >0  :
                await self.birthday_checker(self.bot,self.db)
            logging.info("INFO: task_loop - periodic_check - complete")
        except Exception as Ex:
            logging.error(f"ERROR: task_loop.py - periodic_check() - Exception: {Ex}")
def setup(bot):
    bot.add_cog(TaskLoop(bot))
