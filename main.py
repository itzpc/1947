import logging
import sys
import os 
from application.config.config import DiscordConfig
from application.utlis.coc_utlis import Coc_Config
from bot import Bot1947

class BOTApp():
    def __init__(self):
        self.sql_session = None


    def execute(self):
        try:
            coc_config = Coc_Config()
            coc_client = coc_config.create_client()
            Bot1947(coc_client).run()

        except Exception as Ex:
            logging.error("Exception : {}".format(Ex))


if __name__ == "__main__":
    directory= os.getcwd()
    logging.basicConfig(filename=directory+DiscordConfig.LOG_FILE, level=logging.DEBUG,format='%(asctime)s : %(message)s', datefmt='%m-%d-%Y %I:%M:%S %p')
    logging.info('Logging has started.')
    Bot = BOTApp()
    Bot.execute()