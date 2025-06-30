from dataclasses import dataclass
from typing import Optional
from .connection import get_db

@dataclass
class User:
    telegram_id: int
    username: Optional[str]
    besitos: int = 0
    level: int = 1

@dataclass
class Channel:
    channel_id: int
    title: Optional[str]

async def create_tables():
    query_users = (
        "CREATE TABLE IF NOT EXISTS users ("
        "telegram_id INTEGER PRIMARY KEY,"
        "username TEXT,"
        "besitos INTEGER DEFAULT 0,"
        "level INTEGER DEFAULT 1"
        ")"
    )
    query_channels = (
        "CREATE TABLE IF NOT EXISTS channels ("
        "channel_id INTEGER PRIMARY KEY,"
        "title TEXT"
        ")"
    )
    query_user_channels = (
        "CREATE TABLE IF NOT EXISTS user_channels ("
        "telegram_id INTEGER,"
        "channel_id INTEGER,"
        "PRIMARY KEY (telegram_id, channel_id)"
        ")"
    )
    async with await get_db() as db:
        await db.execute(query_users)
        await db.execute(query_channels)
        await db.execute(query_user_channels)
        await db.commit()
