import coc
from application.config.config import CocConfig

class Coc_Config():

    def __init__(self):
        self.email = CocConfig.EMAIL
        self.password = CocConfig.PASSWORD
    
    def create_client(self):
        return coc.login(self.email,self.password, client=coc.EventsClient, key_names="1947")