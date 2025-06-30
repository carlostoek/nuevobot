import aiosqlite
from config import DATABASE_URL

_db_path = DATABASE_URL.replace('sqlite:///', '')

async def get_db():
    return await aiosqlite.connect(_db_path)
