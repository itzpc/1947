import logging
import sys
import os 
import asyncio
from application.config.config import DiscordConfig, PostgreeDB_Config
from application.utlis.coc_utlis import Coc_Config
from application.database.postgre_db import PostgreDB
from bot import Bot1947

class BOTApp():
    def __init__(self):
        self.sql_session = None
        self.loop = None


    def get_postgre_connection(self):
        loop = asyncio.get_event_loop()
        self.loop=loop
        try:
            self.sql_session = loop.run_until_complete(PostgreDB(PostgreeDB_Config.URI).connect())
            logging.info("Postgree pool connected")
        finally:
            logging.info("Postgree connection complete")


    def execute(self):
        try:
            coc_config = Coc_Config()
            coc_client = coc_config.create_client()
            self.get_postgre_connection()
            if self.sql_session:
                Bot1947(coc_client,self.sql_session).run()

            logging.info("Logging has stopped -------------------------------------------------")
        except Exception as Ex:
            logging.error("Exception : {}".format(Ex))

        finally:
            logging.info("Logging Finally")
            self.loop.stop()


if __name__ == "__main__":
    directory= os.getcwd()
    logging.basicConfig(filename=directory+DiscordConfig.LOG_FILE, level=logging.INFO,format='%(asctime)s : %(message)s', datefmt='%m-%d-%Y %I:%M:%S %p')
    logging.info('Logging has started --------------------------------------------------------')
    Bot = BOTApp()
    Bot.execute()