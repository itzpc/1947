
import asyncio
import asyncpg
import logging
import traceback
from datetime import datetime

class DbUtlis():
    def __init__(self,connection):
        self.conn = connection
        
    async def delete_from_bot_table(self,id):
        try:
            sql = "SELECT left_on FROM BOT where guild_id=($1);"
            value = (id)
            result = await self.conn.fetchrow(sql,value)
            if result:
                if result['left_on']:
                    logging.error(f"BOT has already left guild, guild_id: {id}")
                else:
                    sql = "UPDATE BOT SET left_on =($1) where guild_id=($2);"
                    value=(datetime.utcnow(),id)
                    await self.conn.execute(sql,*value)
                    logging.info(f"BOT has left guild, guild_id: {id}")
                    
            else:
                sql = "INSERT INTO BOT(guild_id) VALUES ($1);"
                await self.conn.execute(sql,value)
                logging.info(f"BOT has joined on guild_id: {id}")
        except :
            logging.error(traceback.format_exc())

    async def insert_into_bot_table(self,id):
        try:
            sql = "SELECT left_on FROM BOT where guild_id=($1);"
            value = (id)
            result = await self.conn.fetchrow(sql,value)
            if result:
                if result['left_on']:
                    sql = "UPDATE BOT SET left_on =($1) where guild_id=($2);"
                    value=(None,id)
                    await self.conn.execute(sql,*value)
                    logging.info(f"BOT has rejoined on guild_id: {id}")
            else:
                sql = "INSERT INTO BOT(guild_id) VALUES ($1);"
                await self.conn.execute(sql,value)
                sql = "INSERT INTO GUILD(guild_id) VALUES ($1);"
                await self.conn.execute(sql,value)
                logging.info(f"BOT has joined on guild_id: {id}")
        except:
            logging.error(traceback.format_exc())

    async def insert_into_member_on_guild_table(self,guildId,memberId):
        try:
            sql = "INSERT INTO GUILD(guild_id) SELECT ($1) WHERE NOT EXISTS (SELECT 1 FROM guild WHERE guild_id=($1));"
            value=(guildId)
            await self.conn.execute(sql,value)
            sql = "INSERT INTO member(member_id) SELECT ($1) WHERE NOT EXISTS (SELECT 1 FROM member WHERE member_id=($1));"
            value = (memberId)
            await self.conn.execute(sql,value)
            sql = "SELECT left_on FROM members_on_guild where guild_id=($1) and member_id = ($2);"
            value=(guildId,memberId)
            result = await self.conn.fetchrow(sql,*value)
            if result:
                if result['left_on']:
                    sql = "UPDATE members_on_guild SET left_on =($1) where guild_id=($2) and member_id = ($2);"
                    value=(None,guildId,memberId)
                    await self.conn.execute(sql,*value)
                    logging.info(f"db_utlis.py - insert_into_member_on_guild_table({guildId},{memberId}) Member has rejoined guild")
            else:
                sql = "INSERT INTO members_on_guild(guild_id,member_id) VALUES ($1,$2);"
                await self.conn.execute(sql,value)
                logging.info(f"db_utlis.py - insert_into_member_on_guild_table({guildId},{memberId}) New Member has joined guild")
        except:
            logging.error(traceback.format_exc())
            
    async def delete_from_member_on_guild_table(self,guildId,memberId):
        try:
            sql = "SELECT left_on FROM members_on_guild where guild_id=($1) and member_id = ($2);"
            value=(guildId,memberId)
            result = await self.conn.fetchrow(sql,*value)
            if result:
                if result['left_on']:
                    logging.error(f"db_utlis.py - delete_from_member_on_guild_table({guildId},{memberId}) Member has already left guild")
                else:
                    sql = "UPDATE members_on_guild SET left_on =($1) where guild_id=($2) and member_id = ($2);"
                    value=(datetime.utcnow(),guildId,memberId)
                    await self.conn.execute(sql,*value)
                    logging.info(f"db_utlis.py - delete_from_member_on_guild_table({guildId},{memberId}) Member has left guild")
                    
            else:
                sql = "INSERT INTO members_on_guild(guild_id,member_id) VALUES ($1,$2);"
                await self.conn.execute(sql,*value)
                sql = "INSERT INTO member(member_id) SELECT ($1) WHERE NOT EXISTS (SELECT 1 FROM member WHERE member_id=($1));"
                value = (memberId)
                await self.conn.execute(sql,value)
                logging.error(f"db_utlis.py - delete_from_member_on_guild_table({guildId},{memberId}) Member has left guild. members_on_guild table new entry added")
        except :
            logging.error(traceback.format_exc())

    async def get_prefix_of_guild(self,id):
        try:
            guild_prefix = list()
            sql = "SELECT prefix FROM GUILD where guild_id = ($1);"
            value = (id)
            result = await self.conn.fetchrow(sql,value)
            return [result['prefix']]
        except:
            logging.error(traceback.format_exc())

    async def get_default_clan_of_guild(self,id):
        try:
            clan_tag = None
            sql = "select clan_tag from (select * from guild,global_clan_list where guild.default_clan_id=global_clan_list.id) AS guildclans where guildclans.guild_id= ($1);"
            value = (id)
            result = await self.conn.fetchrow(sql,value)
            if result:
                clan_tag = result['clan_tag']
                logging.info(f"db_utlis.py - get_default_clan_of_guild({id}) was found{clan_tag}")
                return str(clan_tag)
            else:
                logging.info(f"db_utlis.py - get_default_clan_of_guild({id}) was not found{clan_tag}")
            return None
        except:
            logging.error(traceback.format_exc())

    async def add_default_channel(self,guildId,channelId):
        try:
            sql = "UPDATE guild SET default_channel =($1) where guild_id=($2);"
            value = (channelId,guildId)
            result = await self.conn.execute(sql,*value)
            logging.info(f"db_utlis.py - add_default_channel({guildId},{channelId}) was successfull")
            return
        except:
            logging.error(traceback.format_exc())

    async def get_default_channel(self,guildId):
        try:
            channel = list()
            sql = "SELECT default_channel FROM GUILD where guild_id = ($1);"
            value = (guildId)
            result = await self.conn.fetchrow(sql,value)
            if result:
            
                channel.append(result['default_channel'])
                return channel
            else:
                return None    
        except:
            logging.error(traceback.format_exc())

    async def add_new_public_clan_tag(self,clantag):
        try:
            sql = "SELECT clan_tag FROM public_clan_list where clan_tag=($1);"
            value = (clantag)
            result = await self.conn.fetchrow(sql,value)
            if result:
                logging.info(f"db_utlis.py - add_new_public_clan_tag - Tag already presnet tag{clantag}, Return False")
                return False
            else:
                sql = "INSERT INTO public_clan_list(clan_tag) VALUES ($1);"
                await self.conn.execute(sql,value)
                logging.info(f"db_utlis.py - add_new_public_clan_tag - New clan inserted {clantag}, Return True")
                return True    
        except:
            logging.error(traceback.format_exc())
    async def add_new_global_clan_tag(self,clantag):
        try:
            sql = "SELECT id FROM global_clan_list where clan_tag=($1);"
            value = (clantag)
            result = await self.conn.fetchrow(sql,value)
            if result:
                logging.info(f"db_utlis.py - add_new_global_clan_tag - Tag already presnet tag{clantag}, Return ID: {result['id']}")
                return result
            else:
                sql = "INSERT INTO global_clan_list(clan_tag) VALUES ($1) RETURNING id;"
                result = await self.conn.fetch(sql,value)
                logging.info(f"db_utlis.py - add_new_global_clan_tag - New clan inserted {clantag}, Return ID:{result['id']}")
                return result['id']  
        except:
            logging.error(traceback.format_exc())
    async def add_new_clan_tag(self,guilid,clantag):
        try:
            await self.add_new_public_clan_tag(clantag)
            id = await self.add_new_global_clan_tag(clantag)
            
            if id :
                sql = "SELECT clan_id FROM clans_on_guild where guild_id = ($1) and clan_id = ($2);"
                id = ''.join(map(str, id)) # id is asyncpg.Record Type
                value = (guilid,int(id))
                result = await self.conn.fetchrow(sql,*value)
                logging.info(f"db_utlis.py - add_new_clan_tag  global clan tag return {int(id)} ressult {result}")
                if result:
                    logging.info(f"db_utlis.py - add_new_clan_tag({guilid},{clantag}) - Clan already present")
                else:
                    sql = "INSERT INTO clans_on_guild(guild_id,clan_id)VALUES ($1,$2);"
                    await self.conn.execute(sql,*value)
                    logging.info(f"db_utlis.py - add_new_clan_tag({guilid},{clantag}) - New clan registered.")
                    sql = "UPDATE guild SET default_clan_id =($1) where guild_id=($2);"
                    value = (int(id),guilid)
                    await self.conn.execute(sql,*value)
                    logging.info(f"db_utlis.py - add_new_clan_tag({guilid},{clantag}) - Default clan added.")
                    return    
        except:
            logging.error(traceback.format_exc())

            
    async def list_clans_linked_to_guild(self,guilid):
        try:
            clan_list=list()
            sql = "select guildclans.clan_tag,guildclans.war_log_channel from (select * from clans_on_guild,global_clan_list where clans_on_guild.clan_id=global_clan_list.id) AS guildclans where guildclans.guild_id=($1)";
            value=(guilid)
            result = await self.conn.fetch(sql,value)
            
            if result:
                for record in result:        
                    clan_list.append(record['clan_tag'])
                logging.info(f"db_utlis.py - list_clans_linked_to_guild({guilid}) - return:{clan_list}")
                return clan_list
            else:
                logging.info(f"db_utlis.py - list_clans_linked_to_guild({guilid}) - return: False - {clan_list}")
                return False
        except:
            logging.error(traceback.format_exc())
    
    async def add_war_log_channel(self,guilid,clantag,channelid):
        try:
            clanlist = await self.list_clans_linked_to_guild(guilid)
            if clanlist is None:
                return False
            if clantag in clanlist:
                sql="UPDATE clans_on_guild SET war_log_channel = $1 FROM global_clan_list WHERE clans_on_guild.clan_id = global_clan_list.id AND clans_on_guild.guild_id=$2 and global_clan_list.clan_tag=$3"
                value=(channelid,guilid,clantag)
                await self.conn.execute(sql,*value)
                logging.info(f"db_utlis.py - add_war_log_channel({guilid},{clantag},{channelid}) - return: True")
                return True
            else:
                logging.info(f"db_utlis.py - add_war_log_channel({guilid},{clantag},{channelid}) - return: False")
                return False
        except:
            logging.error(traceback.format_exc())

    async def get_list_of_public_clan_tags(self):
        try:
            clan_list=list()
            sql = "SELECT clan_tag FROm global_clan_list;";
            result = await self.conn.fetch(sql)
            if result:
                for record in result:        
                    clan_list.append(record['clan_tag'])

            logging.info(f"db_utlis.py - get_list_of_public_clan_tags() - return:{clan_list}")
            return clan_list
            
        except:
            logging.error(traceback.format_exc())

    async def get_dict_of_guild_war_log_channel_of_clan(self, clantag):
        try:
            clan_report_dict_list=list()
            sql = "select guildclans.guild_id,guildclans.war_log_channel from (select * from clans_on_guild,global_clan_list where clans_on_guild.clan_id=global_clan_list.id) AS guildclans where guildclans.clan_tag=$1;"
            value=(clantag)
            result = await self.conn.fetch(sql,value)
            if result:
                for record in result:
                    details_dict =dict()
                    details_dict['guild_id']=record['guild_id']
                    details_dict['channel_id']=record['war_log_channel']
                    clan_report_dict_list.append(details_dict)

            logging.info(f"db_utlis.py - get_dict_of_guild_war_log_channel_of_clan({clantag}) - return:{clan_report_dict_list}")
            return clan_report_dict_list
            
        except:
            logging.error(traceback.format_exc())

    async def get_clans_on_guild_information(self,guilid):
        try:
            clan_list=list()
            sql = "select * from (select * from clans_on_guild,global_clan_list where clans_on_guild.clan_id=global_clan_list.id) AS guildclans where guildclans.guild_id=($1)";
            value=(guilid)
            result = await self.conn.fetch(sql,value)
            
            if result:
                
                logging.info(f"db_utlis.py - get_clans_on_guild_information({guilid}) - return:{result}")
                return result
            else:
                logging.info(f"db_utlis.py - get_clans_on_guild_information({guilid}) - return: False - {None}")
                return False
        except:
            logging.error(traceback.format_exc())


    '''
    async def insert_into_bot_table(self,id):
        #sql = f"INSERT INTO BOT(guild_id) VALUES ($1);"
        #await self.conn.execute(sql)

        sql = f"SELECT guild_id,left_on FROM BOT where guild_id=($1);"
        value = (id)
        res = await self.conn.fetchrow(sql,value)
        print(res['guild_id'])
         
        async with self.conn.transaction():
            async for record in self.conn.cursor(sql,value):
                for k,v in record.items():
                    print (f" K: {str(k)} V : {str(v)}" )
    '''   
'''
class Test():
    def __init__(self):
        self.sql_session = None 

    async def database_connection(self):
        uri = "postgresql://postgres:password@localhost:5432/eka1947_db"
        self.sql_session = await asyncpg.connect(uri)
        db = DbUtlis(self.sql_session)
        await db.delete_from_bot_table(55679)

    def get_postgre_connection(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.database_connection())
        


    def execute(self):
        self.get_postgre_connection()
       

if __name__ == "__main__":
    Test().execute()
'''
