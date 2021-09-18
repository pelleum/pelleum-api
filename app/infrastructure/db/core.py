import logging
import databases
from fire_rank.settings import Settings

DATABASE = None


async def get_or_create_database(s: Settings):
    global DATABASE
    if DATABASE is not None:
        return DATABASE

    logging.info("Created DB!")
    DATABASE = databases.DATABASE(s.database_url, min_size=5)
    logging.info("Connected!")
    await DATABASE.connect()
    return DATABASE
