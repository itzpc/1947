import asyncio
import asyncpg
import logging
#sqlalchemy.__version__
class PostgreDB:

    def __init__(self,uri):        
        self.uri =uri
    

    async def connect(self):
        try:
            conn =  await asyncpg.create_pool(self.uri, max_size=85)
            logging.info(f" Db client connection created")
            return conn
        except Exception as dBx:
            logging.error(f" Error in creating connection : {dBx}")

    async def close(self,connection):
        try: 
            await connection.close()
            logging.info("Db client connection closed")
            return
        except Exception as dBx:
            logging.error(f" Error in creating connection : {dBx}")

    async def sample_connection(self):
        try:
            conn =  await asyncpg.connect(self.uri)
            logging.info(f" Db client connection created")
            return conn
        except Exception as dBx:
            logging.error(f" Error in creating connection : {dBx}")