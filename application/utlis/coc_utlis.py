import coc
from application.config.config import CocConfig

class CustomClient(coc.EventsClient):
  def _create_status_tasks(self, cached_war, war):
    if cached_war.state != war.state:
      self.dispatch("on_war_state_change", war.state, war)
    super()._create_status_tasks(cached_war, war)

class Coc_Config():

    def __init__(self):
        self.email = CocConfig.EMAIL
        self.password = CocConfig.PASSWORD
    
    def create_client(self):
        return coc.login(self.email,self.password, client=CustomClient, key_names="1947")