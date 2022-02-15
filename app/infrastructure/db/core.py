import databases

from app.dependencies import logger
from app.settings import settings

DATABASE = None
DATABASE_URL = f"{settings.db_engine}://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

async def get_or_create_database():
    global DATABASE
    if DATABASE is not None:
        return DATABASE

    DATABASE = databases.Database(DATABASE_URL, min_size=5)

    await DATABASE.connect()
    logger.info("Connected to Database!")
    return DATABASE
